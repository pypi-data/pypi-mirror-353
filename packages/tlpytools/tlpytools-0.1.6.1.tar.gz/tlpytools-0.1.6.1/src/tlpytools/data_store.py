import os
import warnings
import pandas as pd
import geopandas as gpd
import shelve
from tlpytools.data import data_tables


class DataStore:
    """Standard data store to be accessed as class objects"""

    def __init__(self):
        self.vars_filename = "tmp/data_store_vars"
        self.dfs_filename_pattern = "tmp/data_store_dfs_{df_name}.fea"
        self.gdfs_filename = "tmp/data_store_gdfs.gpkg"
        self.data_store_write_mode = True
        if not os.path.exists(os.path.dirname(self.vars_filename)):
            os.makedirs(os.path.dirname(self.vars_filename))
        if not os.path.exists(os.path.dirname(self.dfs_filename_pattern)):
            os.makedirs(os.path.dirname(self.dfs_filename_pattern))
        if not os.path.exists(os.path.dirname(self.gdfs_filename)):
            os.makedirs(os.path.dirname(self.gdfs_filename))
        # suppress performance warning for pytables
        warnings.filterwarnings("ignore", category=pd.io.pytables.PerformanceWarning)

    def load_existing_data(self, spec: dict):
        # initialize objects
        vars_obj = {}
        dfs_obj = {}
        gdfs_obj = {}
        if os.path.exists(self.vars_filename + ".dat"):
            vars_store = shelve.open(self.vars_filename)
        else:
            # no files available, return nothing
            print(f"DATA WARNING - data store files are not available.")
            return None, None, None

        # build metadata
        metadata_obj = vars_store["metadata"]
        saved_spec = metadata_obj["spec"]
        current_step = spec["RESUME_AFTER"]
        completed_step = metadata_obj["completed_step"]
        saved_completed_steps = spec["STEPS"][: spec["STEPS"].index(completed_step) + 1]
        current_completed_steps = saved_spec["STEPS"][
            : saved_spec["STEPS"].index(completed_step) + 1
        ]
        if completed_step != current_step:
            # steps do not match, return nothing
            print(
                f"CONFIG WARNING - data file has step {completed_step} but config wants to resume from step {current_step}."
            )
            return None, None, None
        if saved_completed_steps != current_completed_steps:
            # steps do not match, return nothing
            print(
                f"CONFIG WARNING - data file has previous steps {saved_completed_steps} do not match config {current_completed_steps}."
            )
            return None, None, None

        # build data objects
        for var_name in metadata_obj["var_list"]:
            vars_obj[var_name] = vars_store[var_name]
        for df_name in metadata_obj["dfs_list"]:
            input_df_filename = self.dfs_filename_pattern.format(df_name=df_name)
            dfs_obj[df_name] = pd.read_parquet(input_df_filename, engine="pyarrow")
        for gdf_name in metadata_obj["gdf_list"]:
            gdfs_obj[gdf_name] = gpd.read_file(
                self.gdfs_filename, layer=gdf_name, driver="GPKG"
            )
        # check and read additional tables added to spec
        missing_spatials = set(spec["FILES"]["SPATIALS"].keys()).difference(
            set(metadata_obj["gdf_list"])
        )
        query_spec = spec.copy()
        missing_tbls = set(spec["FILES"]["INPUTS"].keys()).difference(
            set(metadata_obj["dfs_list"])
        )
        if len(missing_tbls) > 0:
            query_spec["FILES"]["INPUTS"] = {
                key: query_spec["FILES"]["INPUTS"][key] for key in list(missing_tbls)
            }
            missing_dfs = data_tables.read_tbl_data(s=query_spec)
            for tbl_name in missing_dfs.keys():
                dfs_obj[tbl_name] = missing_dfs[tbl_name].copy()
        if len(missing_spatials) > 0:
            query_spec["FILES"]["SPATIALS"] = {
                key: query_spec["FILES"]["SPATIALS"][key]
                for key in list(missing_spatials)
            }
            missing_gdfs = data_tables.read_spatial_data(s=query_spec)
            for tbl_name in missing_gdfs.keys():
                gdfs_obj[tbl_name] = missing_gdfs[tbl_name].copy()

        # check and load vars object
        for stored_var_name, stored_var_value in spec["VARS"].items():
            if stored_var_name not in list(vars_obj.keys()):
                # warn that new variable values will be inserted
                print(
                    f"CONFIG WARNING - Variables {stored_var_name} is new, so it will be added."
                )
                vars_obj[stored_var_name] = stored_var_value
            if stored_var_value != vars_obj[stored_var_name]:
                # warn if variable values has changed
                print(
                    f"CONFIG WARNING - Variables {stored_var_name} have changed, using saved value {vars_obj[stored_var_name]} instead of {stored_var_value}."
                )

        # close data stores
        vars_store.close()

        # since we have successful resume after data loaded, write mode is now disabled
        self.data_store_write_mode = False

        # return data
        return vars_obj, dfs_obj, gdfs_obj

    def save_all_data(self, vars_obj, dfs_obj, gdfs_obj, current_step: str, spec: dict):
        # skip write if step matches resume after or write mode is False
        if self.data_store_write_mode == False or current_step != spec["RESUME_AFTER"]:
            return False

        # build metadata
        metadata_obj = {
            "var_list": list(vars_obj.keys()),
            "dfs_list": list(dfs_obj.keys()),
            "gdf_list": list(gdfs_obj.keys()),
            "spec": spec,
            "completed_step": current_step,
        }

        # clean up old files
        for file in [
            self.vars_filename + ".bak",
            self.vars_filename + ".dat",
            self.vars_filename + ".dir",
            self.dfs_filename_pattern,
            self.gdfs_filename,
        ]:
            if os.path.exists(file):
                os.remove(file)

        # establish data stores
        vars_store = shelve.open(self.vars_filename)

        # assign data into data stores
        vars_store["metadata"] = metadata_obj
        for var_name in metadata_obj["var_list"]:
            vars_store[var_name] = vars_obj[var_name]
        for df_name in metadata_obj["dfs_list"]:
            export_df_filename = self.dfs_filename_pattern.format(df_name=df_name)
            if os.path.exists(export_df_filename):
                os.remove(export_df_filename)
            # fix data types
            for var_name, inferred_type in (
                (dfs_obj[df_name].apply(pd.api.types.infer_dtype, axis=0))
                .to_dict()
                .items()
            ):
                if "mixed" in inferred_type:
                    data_type = "str"
                elif inferred_type == "decimal":
                    data_type = "float64"
                elif inferred_type == "string":
                    data_type = "str"
                elif inferred_type == "integer":
                    # use float for int in case there are na values
                    data_type = "float64"
                elif inferred_type == "floating":
                    data_type = "float64"
                elif inferred_type == "date":
                    data_type = "datetime64"
                else:
                    data_type = "str"
                dfs_obj[df_name][var_name] = dfs_obj[df_name][var_name].astype(
                    data_type
                )
                # fix non string column names
                if type(var_name) != str:
                    dfs_obj[df_name][str(var_name)] = dfs_obj[df_name][var_name].copy()
                    dfs_obj[df_name] = dfs_obj[df_name].drop(columns=[var_name])

            # export to parquet
            dfs_obj[df_name].to_parquet(export_df_filename, engine="pyarrow")
        for gdf_name in metadata_obj["gdf_list"]:
            gdfs_obj[gdf_name].to_file(
                self.gdfs_filename, layer=gdf_name, driver="GPKG"
            )

        # close and save data stores
        vars_store.close()

        return True
