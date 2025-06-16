from kedro.pipeline import Pipeline, node, pipeline
from kedro.pipeline.modular_pipeline import pipeline

from .nodes import load_and_preprocess_data, join_fake_and_true_data, add_text_column_fast, onion_renaming

#def create_pipeline(**kwargs) -> Pipeline:
#    return pipeline(
#        [
#            node(
#                func=load_and_preprocess_data,
#                inputs=["ali_raza_true", "params:flag_true"],
#                outputs="staging_ali_raza_true",
#                name="staging_ali_raza_true_node",
#            ),
#            node(
#                func=load_and_preprocess_data,
#                inputs=["ali_raza_fake", "params:flag_fake"],
#                outputs="staging_ali_raza_fake",
#                name="staging_ali_raza_fake_node",
#            ),
#            node(
#                func=load_and_preprocess_data,
#                inputs=["bhavik_jikadara_true", "params:flag_true"],
#                outputs="staging_bhavik_jikadara_true",
#                name="staging_bhavik_jikadara_true_node",
#            ),
#            node(
#                func=load_and_preprocess_data,
#                inputs=["bhavik_jikadara_fake", "params:flag_fake"],
#                outputs="staging_bhavik_jikadara_fake",
#                name="staging_bhavik_jikadara_fake_node",
#            ),
#            node(
#                func=join_fake_and_true_data,
#                inputs=["staging_ali_raza_fake", "staging_ali_raza_true"],
#                outputs="ali_raza",
#                name="ali_raza_node",
#            ),
#            node(
#                func=join_fake_and_true_data,
#                inputs=["staging_bhavik_jikadara_fake", "staging_bhavik_jikadara_true"],
#                outputs="bhavik_jikadara",
#                name="bhavik_jikadara_node",
#            ),
#        ]
#    )

# Namespaced Pipeline
def acreate_pipeline(**kwargs) -> Pipeline:
    base_processing = pipeline(
        [
            node(
                func=load_and_preprocess_data,
                inputs=["raw_true", "params:flag_true"],
                outputs="staging_true",
                name="staging_true_node",
            ),
            node(
                func=load_and_preprocess_data,
                inputs=["raw_fake", "params:flag_fake"],
                outputs="staging_fake",
                name="staging_fake_node",
            ),
            node(
                func=join_fake_and_true_data,
                inputs=["staging_fake", "staging_true"],
                outputs="news_data",
                name="news_data_node",
            ),
        ]
    )

    ali_raza_pipeline = pipeline(
        pipe=base_processing,
        inputs={"raw_true": "ali_raza_true", "raw_fake": "ali_raza_fake"},
        parameters={
            "flag_true": "flag_true",
            "flag_fake": "flag_fake",
        },
        namespace="ali_raza"
    )

    bhavik_jikadara_pipeline = pipeline(
        pipe=base_processing,
        inputs={"raw_true": "bhavik_jikadara_true", "raw_fake": "bhavik_jikadara_fake"},
        parameters={
            "flag_true": "flag_true",
            "flag_fake": "flag_fake",
        },
        namespace="bhavik_jikadara"
    )


    return ali_raza_pipeline + bhavik_jikadara_pipeline

def onion_pipeline(**kwargs) -> Pipeline:
    return pipeline(
        [
            #node(
            #    func=add_text_column_fast,
            #    inputs="r_not_the_onion",
            #    outputs="raw_r_not_the_onion_with_text",
            #    name="raw_r_not_the_onion_with_text_node",
            #),
            node(
                func=onion_renaming,
                inputs=["the_onion", "params:onion_column_mapping"],
                outputs="renamed_onion",
                name="renamed_onion_node",
            ),
            node(
                func=onion_renaming,
                inputs=["r_not_the_onion", "params:r_not_the_onion_mapping"],
                outputs="renamed_r_not_the_onion",
                name="renamed_r_not_the_onion_node",
            ),
            node(
                func=load_and_preprocess_data,
                inputs=["renamed_r_not_the_onion", "params:flag_true"],
                outputs="staging_true",
                name="staging_true_node",
            ),
            node(
                func=load_and_preprocess_data,
                inputs=["renamed_onion", "params:flag_fake"],
                outputs="staging_fake",
                name="staging_fake_node",
            ),
            node(
                func=join_fake_and_true_data,
                inputs=["staging_fake", "staging_true"],
                outputs="news_data",
                name="news_data_node",
            ),
        ]
    )