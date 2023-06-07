from shiny import *

app_ui = ui.page_fluid(
    ui.panel_title("Ask Your Docs - DEMO"),
    ui.navset_tab_card(
        ui.nav('Instructions',
               ui.panel_main(
                   "Write the documentation for the application here"
                )
        ),
        ui.nav('Ask',
               ui.layout_sidebar(
                   ui.panel_sidebar(
                       ui.input_text_area('question_input', 'What wisdom do you seek?', rows=4),
                       ui.input_action_button(id="start_process", label="Do Magic", class_='btn-success'),
                       "\n",
                       width=4
                   ),
                   ui.panel_main(
                       ui.panel_conditional(
                           """input.start_process > 0 && && input.questioninput != ''""",
                           ui.output_text('final_answer'),
                        ),
                   width=8,
                   ),
               ),
        ),
        selected='Ask',
    ),
    title='Ask Your Docs',
)





def server(input, output, session):
    @output()
    @render.text
    @reactive.event(input.start_process)
    async def final_answer():
        placeholder_answer = 'Bleep bloop, I do not compute (yet)....'
        return placeholder_answer



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


