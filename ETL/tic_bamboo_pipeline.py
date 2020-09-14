import pandas as pd
import os
import csv

from bamboo_lib.logger import logger
from bamboo_lib.helpers import grab_connector
from bamboo_lib.models import EasyPipeline, PipelineStep, Parameter
from bamboo_lib.steps import LoadStep


VARIABLE_DICT = { 
    1: "Acceso a TIC",
    2: "Acceso a Internet",
    3: "Acceso a TV Cable",
    4: "Tipo de Teléfono",
    5: "Empleó Equipos Informáticos",
    6: "Usó Internet",
    7: "Usó Internet para buscar Productos y Servicios",
    8: "Tuvo Problemas de Electricidad"
}


class OpenStep(PipelineStep):
    def run_step(self, prev, params):
        logger.info("Opening files from source folder...")
        
        df = {i: pd.read_excel("data_source/chart{}.xlsx".format(i)) for i in range(1,9)}
        
        return df


class TidyStep(PipelineStep):
    def run_step(self, prev, params):
        logger.info("Tidying up DataFrame...")

        df = prev

        for i in range(1,9):
            df[i]["region"] = df[i]["region"].str.title()
            
            df[i]["data_origin"] = "INEI" if i in [1,2,3,4] else "ENE"
            
            if i in [1,2,3,4]:
                df[i] = df[i].rename(columns={"censo":"year"})
                df[i]["year"] = df[i]["year"].str[-4:] 
                df[i]["year"] = df[i]["year"].astype(int)
            else:
                df[i]["year"] = 2017
            
            response_col = 2 if i in [1,2,3,4] else 1 
            df[i]["variable"] = VARIABLE_DICT[i]
            df[i]["response"] = df[i].iloc[:, response_col]
            
            df[i] = df[i].rename(columns={"valor_porcentaje": "percentage"})
            
            df[i] = df[i][["region", "data_origin", "year", "variable", "response", "percentage"]]

    
        df_list = [df[i] for i in range(1,9)]
        df = pd.concat(df_list, ignore_index=True)
        df.to_csv("data_temp/tidy_file.csv", index=False, quoting=csv.QUOTE_NONNUMERIC)

        return 0


class RegionDimensionStep(PipelineStep):
    def run_step(self, prev, params):
        logger.info("Creating Region Dimension...")

        df = pd.read_csv("data_temp/tidy_file.csv")

        region_list = list(df["region"].unique())
        df_region = pd.DataFrame({"region_id": list(range(len(region_list))), "region_name": sorted(region_list)})

        return df_region


class VariableDimensionStep(PipelineStep):
    def run_step(self, prev, params):
        logger.info("Creating Variable Dimension...")

        df = pd.read_csv("data_temp/tidy_file.csv")

        df_var = df[["variable", "response"]].copy()

        df_var["combined"] = df_var["variable"] + "|" + df_var["response"]
        df_var = df_var[["combined"]]

        df_var = df_var.drop_duplicates().reset_index(drop=True)

        df_var["response_id"] = df_var.index
        df_var["variable_name"] = df_var["combined"].str.split("|").str[0]
        df_var["response_name"] = df_var["combined"].str.split("|").str[1]

        df_var = df_var[["response_id", "variable_name", "response_name", "combined"]]

        return df_var


class FactTableStep(PipelineStep):
    def run_step(self, prev, params):
        logger.info("Creating Fact Table...")

        df = pd.read_csv("data_temp/tidy_file.csv")

        df_reg = pd.read_csv("data_output/tic_dim_region.csv")
        region_map = {k:v for (k,v) in zip(df_reg["region_name"], df_reg["region_id"])}
        df["region_id"] = df["region"].map(region_map)

        origin_map = {"INEI": 1, "ENE": 0}
        df["data_origin_id"] = df["data_origin"].map(origin_map)

        df_var = pd.read_csv("data_output/tic_dim_variable.csv")
        variable_map = {k:v for (k,v) in zip(df_var["combined"], df_var["response_id"])}
        df["combined"] = df["variable"] + "|" + df["response"]
        df["response_id"] = df["combined"].map(variable_map)

        df = df[["region_id", "data_origin_id", "response_id", "year", "percentage"]]

        return df


class TICPipeline(EasyPipeline):
    @staticmethod
    def parameter_list():
        return [
            Parameter("output-db", dtype=str),
            Parameter("ingest", dtype=bool)
        ]

    @staticmethod
    def steps(params):
        db_connector = grab_connector(__file__, params.get("output-db"))

        open_step = OpenStep()
        tidy_step = TidyStep()

        region_step = RegionDimensionStep()
        load_region = LoadStep(
            table_name="tic_dim_region", 
            connector=db_connector, 
            if_exists="drop", 
            pk=["region_id"],
            dtype={"region_id":"UInt8","region_name":"String"},
            nullable_list=[]
        )

        variable_step = VariableDimensionStep()
        load_variable = LoadStep(
            table_name="tic_dim_variable", 
            connector=db_connector, 
            if_exists="drop", 
            pk=["response_id"],
            dtype={"response_id":"UInt8","variable_name":"String","response_name":"String","combined":"String"},
            nullable_list=[]
        )

        fact_step = FactTableStep()
        load_fact = LoadStep(
            table_name="tic_fact", 
            connector=db_connector, 
            if_exists="drop", 
            pk=["region_id"],
            dtype={"region_id":"UInt8","data_origin_id":"UInt8","response_id":"UInt8","year":"UInt8","percentage":"Float64"},
            nullable_list=[]
        )

        if params.get("ingest")==True:
            steps = [open_step, tidy_step, region_step, load_region, variable_step, load_variable, fact_step, load_fact]
        else:
            steps = [open_step, tidy_step, region_step, variable_step, fact_step]

        return steps


if __name__ == "__main__":
    tic_pipeline = TICPipeline()
    tic_pipeline.run(
        {
            "output-db": "clickhouse-local",
            "ingest": True
        }
    )