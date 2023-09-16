from shiny import App
from shiny import ui
from shiny import render
from shiny import reactive

import re

import askyourdocs.utils as utl
from askyourdocs.settings import SETTINGS as settings
from askyourdocs.pipeline.pipeline import QueryPipeline, IngestionPipeline

environment = utl.load_environment()
_INGESTION_PIPELINE = IngestionPipeline(environment=environment, settings=settings)
_QUERY_PIPELINE = QueryPipeline(environment=environment, settings=settings)

app_ui = ui.page_fluid(
    ui.panel_title("Ask Your Docs - DEMO"),
    ui.navset_tab_card(
        ui.nav('Instructions',
               ui.panel_main(
                   ui.markdown(
                       """
                       Welcome to **Ask Your Documents**, an open source project by the Interagency LLM Taskforce.

                       The goal is to make the power of *Large Language Models* (LLMs) available  to
                       governmental institutions and  
                       other privacy aware agencies by allowing them to host their own instance of this open source
                       application.  
                       Many LLMs are readily available online for *free* but come with the 
                       hidden cost of storing your data. This is  
                       no option for any institution that is concerned
                       with privacy. Instead, *Ask your Documents* uses a locally hosted   
                       database and
                       publicly available LLMs to ensure that no data is sent to or stored by a third party.

                       The demo of this app is divided into two sections:

                        * **Ask Database**:  
                            You can ask questions to all documents already in your database.  
                             - post your question in the text input field, for example:  
                             - '*Which vaccines can be found in the database?* ' and press the *Do Magic* button  
                             - after the calculations are finished the answer will appear on the right side  
                            <br>

                            *Number of chunks* : increase the number of chunks to improve the results, decrease to speed up the process

                        * **Ask File**:  
                            Allows you to upload one or multiple PDF documents and start asking questions about your documents.  
                             - post your question in the text input field, for example:  
                             - '*Which vaccines can be found in the document?* ' and press the *Do Magic* button  
                             - after the calculations are finished the answer will appear on the right side  
                            <br>

                            If you upload more than one document your questions will be sent to all documents
                            selected.

                            *Number of chunks* : increase the number of chunks to improve the results, decrease to speed up the process

                        For questions and feedback, please reach out to: *llm@taskforce.com*
                       """
                   )
                )
        ),
        ui.nav('Ask Database',
               ui.layout_sidebar(
                   ui.panel_sidebar(
                       ui.input_text_area('question_input_db', 'What wisdom do you seek from the database?', rows=4),
                       ui.input_slider('n_chunks_db', 'Number of chunks', min=1, max=5, value=3),
                       ui.input_action_button(id="run_process_db", label="Do Magic", class_='btn-success'),
                       "\n",
                       width=4
                   ),
                   ui.panel_main(
                       ui.panel_conditional(
                           """input.run_process_db > 0 && input.question_input_db != ''""",
                           ui.output_text('get_answer_db'),
                        ),
                   width=8,
                   ),
                ),
        ),
        ui.nav('Ask File',
               ui.layout_sidebar(
                   ui.panel_sidebar(
                       ui.input_file('document_input_file',
                                     'Select a PDF file you wish to ask a question about',
                                     multiple=False, accept='.pdf', button_label='Select',
                                     placeholder='Your PDF here..'),
                       ui.input_text_area('question_input_file', 'What wisdom do you seek from this file?', rows=4),
                       ui.input_slider('n_chunks_file', 'Number of chunks', min=1, max=5, value=3),
                       ui.input_action_button(id="run_process_file", label="Do Magic", class_='btn-success'),
                       "\n",
                       width=4
                   ),
                   ui.panel_main(
                       ui.panel_conditional(
                           """input.run_process_file > 0 && input.question_input_file != ''""",  # && input.document_input_file != null
                           ui.output_text('get_answer_file'),
                        ),
                   width=8,
                   ),
               ),
        ),
        selected='Ask Database',
    ),
    title='Ask Your Docs',
)


def server(input, output, session):

    val = reactive.Value(3)
    @reactive.Effect
    @reactive.event(input.n_chunks_db)
    def _():
        val.set(input.n_chunks_db())

    val = reactive.Value(3)
    @reactive.Effect
    @reactive.event(input.n_chunks_file)
    def _():
        val.set(input.n_chunks_file())

    @output()
    @render.text
    @reactive.event(input.run_process_db)
    async def get_answer_db():
        text = input.question_input_db()
        answer = _QUERY_PIPELINE.apply(text=text)
        answer = re.sub('^<pad>\s*', '', answer)
        answer = re.sub('\s*</s>$', '', answer)
        return answer

    @output()
    @render.text
    @reactive.event(input.run_process_file)
    async def get_answer_file():
        text = input.question_input_db()
        answer = _QUERY_PIPELINE.apply(text=text)
        answer = re.sub('^<pad>\s*', '', answer)
        answer = re.sub('\s*</s>$', '', answer)
        return answer


#####################################################################
# App
#####################################################################
debug = settings['shiny_app']['debug_mode']
app = App(app_ui, server, debug=debug)

#########################################################################################
# run the code below in the python console to start the dashboard.
# first you need to define the ui and server elements (select all code and run it once)

#########################################################################################
# run_app(host='127.0.0.1', port=8000, autoreload_port=0, reload=False,  # ws_max_size=16777216,
#         log_level=None,
#         factory=False, launch_browser=True)
