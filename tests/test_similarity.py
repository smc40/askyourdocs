from askyourdocs.settings import SETTINGS as settings
from askyourdocs.pipeline.pipeline import QueryPipeline
from askyourdocs import Environment
from askyourdocs.modelling.llm import Summarizer


if __name__ == "__main__":
    
    # execute in shell: export PYTHONPATH="/home/bouldermaettel/Documents/python-projects/askyourdocs:$PYTHONPATH"
    
    Environment.solr_url = "http://localhost:8983"
    Environment.zk_urls = "http://localhost:2181"
    
    query_pipeline = QueryPipeline(environment=Environment, settings=settings)
    question = "ist die covid spritze wirksam und sicher?"

    # results = query_pipeline._get_knn_vecs_from_text(text="is there an appropriate model for more than 512 tokens?")
    results = query_pipeline._get_knn_vecs_from_text(text=question)
    print([result.get('score') for result in results])
    result_text = query_pipeline._get_text_entities_from_knn_vecs(knn_vecs=results)
    text = query_pipeline._get_context_from_text_entities(text_entities=result_text)
    print(text)
    
    summarizer = Summarizer(settings=settings)
    context = text
    answer = summarizer.get_answer(query=question, context=context)
    print(answer) 