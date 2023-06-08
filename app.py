from shiny import *
import PyPDF2
import re
from pipelines import embedding_loaded_pdf, pipeline_return_question_and_answer
db_items = embedding_loaded_pdf(file_path='docs/20211203_SwissPAR_Spikevax_single_page_text.pdf', chunk_size=200, overlap=10)

app_ui = ui.page_fluid(
    ui.panel_title("Ask Your Docs - DEMO"),
    ui.navset_tab_card(
        ui.nav('Instructions',
               ui.panel_main(
                   "Write the documentation for the application here"
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
        answer = pipeline_return_question_and_answer(query=input.question_input_db(),
                                                     db_items=db_items,
                                                     n_chunks=input.n_chunks_file())
        answer = re.sub('^<pad>\s+', '', answer)
        answer = re.sub('\s+</s>$', '', answer)
        return answer

    @output()
    @render.text
    @reactive.event(input.run_process_file)
    async def get_answer_file():
        db_items = embedding_loaded_pdf(file_path=input.document_input_file()[0]['datapath'], chunk_size=200, overlap=10)
        answer = pipeline_return_question_and_answer(query=input.question_input_db(),
                                                     db_items=db_items,
                                                     n_chunks=input.n_chunks_file())
        answer = re.sub('^<pad>\s+', '', answer)
        answer = re.sub('\s+</s>$', '', answer)
        return answer


#####################################################################
# App
#####################################################################
app = App(app_ui, server, debug=True)




#########################################################################################
# run the code below in the python console to start the dashboard.
# first you need to define the ui and server elements (select all code and run it once)

#########################################################################################
# run_app(host='127.0.0.1', port=8000, autoreload_port=0, reload=False,  # ws_max_size=16777216,
#         log_level=None,
#         factory=False, launch_browser=True)


