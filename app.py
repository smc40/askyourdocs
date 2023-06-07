from shiny import *
import PyPDF2


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
                       ui.input_action_button(id="run_process_file", label="Do Magic", class_='btn-success'),
                       "\n",
                       width=4
                   ),
                    ################################### doesnt work yet ###################################
                   # ui.panel_conditional(
                   #      #"""input.document_input_file != None""",  # 'not None'
                   #     """output.contents === True""",
                   #     ui.input_text_area('question_input_file', 'What wisdom do you seek from this file?', rows=4),
                   #     ui.input_action_button(id="run_process_file", label="Do Magic", class_='btn-success'),
                   #     "\n",
                   # ),
                   ui.panel_main(
                       ui.panel_conditional(
                           """input.run_process_file > 0 && input.question_input_file != ''""",  # && input.document_input_file != null
                           ui.output_text('get_answer_file'),
                           #ui.output_text('test'),
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

    @output()
    @render.text
    @reactive.event(input.run_process_db)
    async def get_answer_db():
        placeholder_answer = 'Bleep bloop, I do not compute (yet)....'
        return placeholder_answer


    @output()
    @render.text
    @reactive.event(input.run_process_file)
    async def get_answer_file():
        """ Currently returns the length of the PDF, not any other document info...
        """
        # placeholder_answer = 'Bleep bloop, I do not compute (yet)....'
        # return placeholder_answer
        print(str(input.document_input_file()))
        pdfFileObj = open(input.document_input_file()[0]['datapath'], 'rb')
        pdfReader = PyPDF2.PdfReader(pdfFileObj)
        num_pages = str(len(pdfReader.pages))
        return num_pages


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


