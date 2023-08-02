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
                       ui.input_file('document_input_files',
                                     'Select one or more PDF file(s) you wish to ask a question about',
                                     multiple=True, accept='.pdf', button_label='Select',
                                     placeholder='Your PDF here..'),
                       ui.input_checkbox_group('selected_files', '', []),
                       # TODO: Hide remove button behind panel_conditional when no file is uploaded yet
                       ui.input_action_button('remove_selected', label="Remove selected PDF(s)"),
                       ui.input_text_area('question_input_file', 'What wisdom do you seek from this file?', rows=4),
                       ui.input_slider('n_chunks_file', 'Number of chunks', min=1, max=5, value=3),
                       ui.input_action_button(id="run_process_file", label="Do Magic", class_='btn-success'),
                       "\n",
                       width=4
                   ),
                   ui.panel_main(
                       ui.panel_conditional(
                           """input.run_process_file > 0 && input.question_input_file != ''""",  # && input.document_input_files != null
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

    documents = reactive.Value([])

    @reactive.Effect
    @reactive.event(input.document_input_files)
    def _():
        docs = documents.get()
        document_names = [ file['name'] for file in docs ]
        
        for file in input.document_input_files():
            if file['name'] not in document_names:
                docs.append(file)
        documents.set(docs)

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
        answer = re.sub('^<pad>\s*', '', answer)
        answer = re.sub('\s*</s>$', '', answer)
        return answer

    @reactive.Effect
    @reactive.event(input.document_input_files)
    def _():
        """
        Update checkbox_group after uploading file(s).
        """
        docs = documents.get()
        choices = [ file['name'] for file in docs ]
        ui.update_checkbox_group('selected_files', label="Selected file(s):", choices=choices, selected=choices)

    @reactive.Effect
    @reactive.event(documents.get)
    def _():
        """
        Update checkbox_group after deleting file(s).
        """
        docs = documents.get()
        choices = [ file['name'] for file in docs ]
        if choices:
            label = "Selected file(s):"
        else:
            label = ""
        ui.update_checkbox_group('selected_files', label=label, choices=choices, selected=[])
        # Use this to auto select remaining documents after deletion
        # ui.update_checkbox_group('selected_files', label=label, choices=choices, selected=choices)

    @reactive.Effect
    @reactive.event(input.remove_selected)
    def _():
        """
        Remove selected file(s).
        """
        docs = documents.get()
        docs_to_keep = [ file for file in docs if file['name'] not in input.selected_files() ]
        # Use this to keep not selected files
        # docs_to_keep = [ file for file in docs if file['name'] in input.selected_files() ]
        documents.set(docs_to_keep)

    @output()
    @render.text
    @reactive.event(input.run_process_file)
    async def get_answer_file():
        db_items = []

        docs = documents.get()

        for file in docs:
            if file['name'] in input.selected_files():
                file['db_items'] = embedding_loaded_pdf(file_path=input.document_input_files()[0]['datapath'], chunk_size=200, overlap=10)
                db_items.extend(file['db_items'])

        answer = pipeline_return_question_and_answer(query=input.question_input_file(),
                                                     db_items=db_items,
                                                     n_chunks=input.n_chunks_file())
        answer = re.sub('^<pad>\s*', '', answer)
        answer = re.sub('\s*</s>$', '', answer)
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


