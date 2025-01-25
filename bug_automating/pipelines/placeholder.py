class Placeholder:
    # action######################################################
    TAP = 'tap'
    LONG_TAP = 'long-tap'
    DOUBLE_TAP = 'double-tap'
    INPUT = 'input'
    SCROLL = 'scroll'
    SCROLL_DIRECTION = 'SCROLL_DIRECTION'
    SCROLL_UP = 'up'
    SCROLL_DOWN = 'down'
    SCROLL_LEFT = 'left'
    SCROLL_RIGHT = 'right'
    HOME = 'home'
    ENTER = 'enter'
    LANDSCAPE = 'landscape'
    PORTRAIT = 'portrait'

    ACTION = 'ACTION'
    ACTIONS = 'ACTIONS'
    ACTIONS_INFO = [TAP, LONG_TAP, DOUBLE_TAP, INPUT, SCROLL, HOME, ENTER, LANDSCAPE, PORTRAIT]

    APP_DIR = 'APP_DIR'
    SCREENSHOT_OPERATION_LIST = 'SCREENSHOT_OPERATION_LIST'
    OUTPUT_LIST = 'OUTPUT_LIST'
    PLANNER_OUTPUT = 'PLANNER_OUTPUT'
    PLANNER_COST = 'PLANNER_COST'
    PLAYER_VERIFIER_OUTPUT_LIST = 'PLAYER_VERIFIER_OUTPUT_LIST'
    PLAYER_OUTPUT = 'PLAYER_OUTPUT'
    VERIFIER_OUTPUT = 'VERIFIER_OUTPUT'

    COST = 'COST'

    SUB_STEP = 'SUB_STEP'
    SUB_STEPS = 'SUB_STEPS'
    STEP = 'STEP'
    STEPS = 'STEPS'
    ORACLES = 'ORACLES'
    OPERATION = 'OPERATION'
    OPERATIONS = 'OPERATIONS'
    SCREENSHOT = 'SCREENSHOT'
    WITH_NUMS = '_with_nums'
    SCREENSHOT_WITH_NUMS = 'SCREENSHOT_WITH_NUMS'
    # OPERATION_SCREENSHOT_DICT = {OPERATION: "{operation}", SCREENSHOT: "screenshot_name"}

    PREVIOUS_STEP = 'PREVIOUS_STEP'
    PREVIOUS_STEP_NUM = 'PREVIOUS_STEP_NUM'
    PREVIOUS_STEP_COMPLETION = 'PREVIOUS_STEP_COMPLETION'
    CURRENT_STEP = 'CURRENT_STEP'
    CURRENT_STEP_NUM = 'CURRENT_STEP_NUM'
    STEP_NO = 'STEP_NO'
    STEP_COMPLETION = 'STEP_COMPLETION'
    NEXT_STEP_NO = 'NEXT_STEP_NO'
    ELEMENT_NUM = 'ELEMENT_NUM'
    ELEMENT_NAME = 'ELEMENT_NAME'
    ELEMENT_CATEGORY = 'ELEMENT_CATEGORY'
    ELEMENT_INPUT = 'ELEMENT_INPUT'
    # CURRENT_STEP_COMPLETION = 'CURRENT_STEP_COMPLETION'
    ALL_STEPS_COMPLETION = 'ALL_STEPS_COMPLETION'

    MISSING_STEP = 'MISSING_STEP'
    COMPOUND_STEP = 'COMPOUND_STEP'

    CHAIN_OF_THOUGHTS = "CHAIN_OF_THOUGHTS"
    ANSWER = "ans"

    ELEMENT_LOCATOR_OUTPUT_FORMAT = {
        # PLAYER_OUTPUT: {
        # CHAIN_OF_THOUGHTS: "The logical reasoning required to identify which actions need to be performed, "
        #                    "which specific element to perform on this GUI.",
        STEP: "Current step's text",
        ACTION: "Specifies the type of action to perform.",
        SCROLL_DIRECTION: f"{SCROLL_UP}, {SCROLL_DOWN}, {SCROLL_LEFT} or {SCROLL_RIGHT}",
        ELEMENT_NAME: "Corresponds to the text description of the element in the GUI.",
        ELEMENT_CATEGORY: "Corresponds to the category of the element in the GUI, such as button, icon, checkbox, "
                          "radiobutton, dropdown menu, slider, link, tab,textfield, ...",
        # ELEMENT_CATEGORY: "Corresponds to the category of the element in the GUI.",
        ELEMENT_NUM: "A number corresponding to the numerical identifier of the element in the GUI.",
        ELEMENT_INPUT: "Specifies the input into the element if needed.",
        # }

        # # PREVIOUS_STEP_NUM: "Describes the number of previous step of the process.",
        # # PREVIOUS_STEP_COMPLETION: "True or False. Indicates whether the previous step has been completed or not.",
        # # STEP_NO: "Describes the number of current step of the process.",
        # STEP: "The current step.",
        # # MISSING_STEP: "The missing step. Indicates whether any step required to complete the current process is missing.",
        # # COMPOSITE_STEP: "True or False. Indicates whether the current step is composed of multiple sub-steps.",
        # # SUB_STEPS: "The sub-steps which need to complete the composite step.",
        # # STEP_COMPLETION: "True or False. Indicates whether the step has been completed or not.",
        # # SUB_STEP: "Describes the sub-step currently being executed based on the GUI, "
        # #           "since the step may require multiple sub-steps to complete.",
        # ACTION: "Specifies the type of action to perform.",
        # SCROLL_DIRECTION: f"{SCROLL_UP}, {SCROLL_DOWN}, {SCROLL_LEFT} or {SCROLL_RIGHT}",
        # ELEMENT_NAME: "Corresponds to the text description of the element in the GUI.",
        # ELEMENT_CATEGORY: "Corresponds to the category of the element in the GUI, such as button, icon, checkbox, "
        #                   "radiobutton, dropdown menu, slider, link, tab,textfield, ...",
        # # ELEMENT_CATEGORY: "Corresponds to the category of the element in the GUI.",
        # ELEMENT_NUM: "Corresponds to the numerical identifier of the element in the GUI.",
        # ELEMENT_INPUT: "Specifies the input into the element if needed.",
        # # ALL_STEPS_COMPLETION: "True or False. Indicates whether all steps have been completed or not."
    }

    STEP_IDENTIFIER = {
        CHAIN_OF_THOUGHTS: "The logical reasoning required to identify.",
        STEP_NO: "Describes the number of current step of the process.",
        MISSING_STEP: ["", ],
        SUB_STEPS: ["", ],
        # STEP_COMPLETION: "True or False. Indicates whether the step has been completed or not.",
        # NEXT_STEP_NO: "Specifies the next step number, which needs to operate."
    }

    STEP_COMPLETER = {
        CHAIN_OF_THOUGHTS: "The logical reasoning required to identify if the step is completed by the GUI.",
        STEP_NO: "Describes the number of current step of the process.",
        STEP_COMPLETION: "True or False. Indicates whether the step has been completed or not.",
        NEXT_STEP_NO: "Specifies the next step number, which needs to operate."
    }
    BUG = "BUG"
    BUGS = "BUGS"
    SUMMARY = "SUMMARY"
    PRECONDITIONS = "PRECONDITIONS"
    STEPS_TO_REPRODUCE = "STEPS_TO_REPRODUCE"
    EXPECTED_BEHAVIORS = "EXPECTED_BEHAVIORS"
    ACTUAL_BEHAVIORS = "ACTUAL_BEHAVIORS"
    STEP_NOS = "STEP_NOS"
    GUI_NUMS = "GUI_NUMS"
    STEP_VERIFICATION = "STEP_VERIFICATION"

    EXECUTION_NUM = 'EXECUTION_NUM'

    # OPERATION_DETAILS = {
    #     ACTION: "",
    #     ELEMENT_NUM: "",
    #     ELEMENT_INPUT: "",
    # }
    #
    # OPERATION_HISTORY = {
    #     OPERATION_DETAILS: OPERATION_DETAILS,
    #     COUNT: "",
    # }
    #
    # STEP_HISTORY = {
    #     STEP_NUM: '',
    #     STEP: '',
    #     OPERATIONS: OPERATION_HISTORY
    # }
    #
    # PLAYER_HISTORY = 'PLAYER_HISTORY'
    STEP_HISTORY_LIST = 'STEP_HISTORY_LIST'
    PREVIOUS_STEP_HISTORY = 'PREVIOUS_STEP_HISTORY'
    OPERATION_HISTORY = 'OPERATION_HISTORY'
    OPERATION_HISTORY_LIST = 'OPERATION_HISTORY_LIST'
    FREQUENCY = "FREQUENCY"

    STEP_HISTORY_LIST_FORMAT = {
        STEP_HISTORY_LIST: [
            {
                STEP: "",
                OPERATION_HISTORY_LIST: [
                    {
                        ACTION: "",
                        ELEMENT_NUM: "",
                        ELEMENT_INPUT: "",
                        SCROLL_DIRECTION: "",
                        EXECUTION_NUM: "Number of times the operation is executed",
                    }
                ]
            }
        ]
    }
    #
    # PLAYER_HISTORY = {
    #     STEP_HISTORY_LIST = [OPERATION_DETAILS],
    #                         PREVIOUS_STEP: STEP_HISTORY
    # }

    # KG constuction
    BUG_ID_LOWER = "bug_id"
    BUG_ID = "BUG_ID"
    REFERENCE = 'REFERENCE'
    RETRIEVAL_RESULT = "RETRIEVAL_RESULT"
    RETRIEVAL_OUTPUT = {
        CHAIN_OF_THOUGHTS: "",
        RETRIEVAL_RESULT: [
            {
                STEPS: [],
                # REFERENCE: f"referenced {BUG_ID}",
            }
        ]
    }
    # PLANNER_RESULT = 'PLANNER_RESULT'
    CLUSTER = "CLUSTER"
    CLUSTER_INDEX = "CLUSTER_INDEX"
    CLUSTER_INDEXES = "CLUSTER_INDEXES"
    REFERENCED_BUG_IDS = 'REFERENCED_BUG_IDS'
    STEP_WITH_CLUSTER_INDEX_FORMAT = '{' \
                                     f'{STEP}: "", {CLUSTER_INDEX}: ""' \
                                     '}'
    # STEP_FORMAT = '{' \
    #               f'{STEP}: ""' \
    #               '}'
    STEP_WITH_CLUSTER_INDEX_REFERENCE_FORMAT = '{' \
                                               f'{STEP}: "", {CLUSTER_INDEX}: [], {REFERENCED_BUG_IDS}: []' \
                                               '}'
    PLANNER_OUTPUT_FORMAT = {
        # f"{CURRENT_STEP}": "Return the step to be executed. If all steps are complete, return None.",
        # f"{SUB_STEPS}": [f"Sub-steps for {CURRENT_STEP}. If all steps are complete, return None."],
        f"{CURRENT_STEP}": "Represents the step that needs to be executed next. "
                           "If there are no more steps, this should be an empty string.",
        f"{SUB_STEPS}": ["A list of sub-steps related to the current step. "
                         "If no sub-steps are left, this should be an empty list.", ],
        f"{ALL_STEPS_COMPLETION}": "True or False. "
                                   f"It should be True only when both {CURRENT_STEP} and {SUB_STEPS} are empty, "
                                   f"indicating that all steps have been completed."
    }

    CREATIVE_THINKING_ORACLES = "CREATIVE_THINKING_ORACLES"
    STEP_WITH_CLUSTER_INDEX_ORACLES_FORMAT = '{' \
                                             f'{STEP}: "", {CLUSTER_INDEX}: [], ' \
                                             f'{ORACLES}: ["", ]' \
                                             '}'
    EXECUTED_STEP = "EXECUTED_STEP"
    CONCISE_STEP = "CONCISE_STEP"
    REPRESENTATIVE_STEP = "REPRESENTATIVE_STEP"
    REPRESENTATIVE_STEPS = "REPRESENTATIVE_STEPS"
    CLUSTERS = "CLUSTERS"
    # ORACLE_FINDER_OUTPUT_FORMAT = {
    #             CHAIN_OF_THOUGHTS: "",
    #             EXECUTED_STEP: "",
    #             CLUSTER_INDEXES: [],
    #             ORACLES: ["", ],
    # }

    # ORACLE_FINDER_OUTPUT_FORMAT = {
    #             CHAIN_OF_THOUGHTS: "",
    #             EXECUTED_STEP: "",
    #             ORACLES: ["", ],
    #             CREATIVE_THINKING_ORACLES: ["", ]
    # }
    ORACLE_FINDER_COST = "ORACLE_FINDER_COST"
    ORACLE_FINDER_OUTPUT = "ORACLE_FINDER_OUTPUT"
    ORACLE_FINDER_OUTPUT_FORMAT = {
        # CHAIN_OF_THOUGHTS: "",
        # EXECUTED_STEP: "",
        CLUSTERS: ["", ],
        ORACLES: ["", ],
    }

    CLUSTER_OUTPUT_FORMAT = {
        CLUSTER_INDEX: "",
        REPRESENTATIVE_STEPS: ["", ],
    }

    # CLUSTER_OUTPUT_FORMAT = {
    #     CLUSTER: "",
    #     REPRESENTATIVE_STEPS: ["", ],
    # }

    CLUSTER_IDENTIFIER_OUTPUT_FORMAT = {
        # CHAIN_OF_THOUGHTS: "",
        # EXECUTED_STEP: "",
        CLUSTERS: [CLUSTER_OUTPUT_FORMAT, ],
        # ORACLES: ["", ],
    }

    STEP_IDENTIFIER_OUTPUT_FORMAT = {
        CHAIN_OF_THOUGHTS: "",
        EXECUTED_STEP: "",
        STEPS: ["", ],
        # ORACLES: ["", ],
    }

    # VERIFIER_OUTPUT_FORMAT = {
    #     # STEP_VERIFICATION: {
    #     #     CHAIN_OF_THOUGHTS: "",
    #     #     STEP_COMPLETION: "True or False. Indicates whether the step has been completed or not."
    #     # },
    #     BUGS: [
    #         {
    #             CHAIN_OF_THOUGHTS: "",
    #             EXECUTED_STEP: "",
    #             ORACLES: ["", ],
    #             CREATIVE_THINKING_ORACLES: ["", ],
    #             SUMMARY: "The summary of bug",
    #             STEPS_TO_REPRODUCE: ["steps to reproduce the bug", ],
    #             EXPECTED_BEHAVIORS: "Expected behaviors",
    #             ACTUAL_BEHAVIORS: "Actual behaviors",
    #             STEP_NOS: "The numbers of relevant steps",
    #             GUI_NUMS: "The numbers of relevant GUIs", },
    #     ]
    #
    # }
    BUG_TYPE = 'BUG_TYPE'
    BUG_SEVERITY = 'BUG_SEVERITY'
    CONFIDENCE = 'CONFIDENCE'
    FORMAT_VERIFIER_COST = "FORMAT_VERIFIER_COST"
    VERIFIER_OUTPUT_FORMAT = {
        # CHAIN_OF_THOUGHTS: "",
        CREATIVE_THINKING_ORACLES: ["", ],
        BUGS: [
            {
                # EXECUTED_STEP: "",
                # ORACLES: ["", ],
                CONFIDENCE: 'The confidence level that this found bug is a real bug, rated from 1 (weakly confident) to 5 (strongly confident)',
                BUG_TYPE: "Enhancement or Defect",
                # @todo add definition: https://wiki.mozilla.org/BMO/UserGuide/BugFields#bug_type
                # BUG_SEVERITY: "Warning or Error",
                SUMMARY: "The summary of bug",
                # PRECONDITIONS: "The preconditions to reproduce bug",
                STEPS_TO_REPRODUCE: ["steps to reproduce the bug", ],
                EXPECTED_BEHAVIORS: "Expected behaviors",
                ACTUAL_BEHAVIORS: "Actual behaviors",
                # STEP_NOS: "The numbers of relevant steps",
                # GUI_NUMS: "The numbers of relevant GUIs",
            },
        ]
    }

    VERIFIER_OUTPUT_FORMAT_WO_ORACLES = {
        # STEP_VERIFICATION: {
        #     CHAIN_OF_THOUGHTS: "",
        #     STEP_COMPLETION: "True or False. Indicates whether the step has been completed or not."
        # },
        BUGS: [
            {
                CHAIN_OF_THOUGHTS: "",
                EXECUTED_STEP: "",
                # ORACLES: ["", ],
                CREATIVE_THINKING_ORACLES: ["", ],
                SUMMARY: "The summary of bug",
                STEPS_TO_REPRODUCE: ["steps to reproduce the bug", ],
                EXPECTED_BEHAVIORS: "Expected behaviors",
                ACTUAL_BEHAVIORS: "Actual behaviors",
                STEP_NOS: "The numbers of relevant steps",
                GUI_NUMS: "The numbers of relevant GUIs", },
        ]

    }

    # INPUT = "INPUT"
    OUTPUT = "OUTPUT"
    SUMMARY = 'SUMMARY'
    DESCRIPTION = 'DESCRIPTION'
    # PRECONDITIONS = 'PRECONDITIONS'
    STEPS_TO_REPRODUCE = 'STEPS_TO_REPRODUCE'
    EXPECTED_RESULTS = 'EXPECTED_RESULTS'
    ACTUAL_RESULTS = 'ACTUAL_RESULTS'
    NOTES = 'NOTES'
    AFFECTED_VERSIONS = 'AFFECTED_VERSIONS'
    AFFECTED_PLATFORMS = 'AFFECTED_PLATFORMS'
    OTHERS = 'OTHERS'
    # add extra parts
    ATTACHMENTS = 'ATTACHMENTS'
    BACKGROUNDS = 'BACKGROUNDS'
    TASKS = 'TASKS'

    # STEP_NO = 'STEP_NO'  # step_num?
    STEP_CLUSTER = 'STEP_CLUSTER'
    STEP_TYPE = 'STEP_TYPE'
    STEP_TYPE_ACTION = 'ACTION'
    # STEP_TYPE_VERIFICATION = 'VERIFICATION'
    STEP_TYPE_CHECK = 'CHECK'

    SCENARIO = 'TEST_SCENARIO'
    SCENARIOS = 'TEST_SCENARIOS'
    SCENARIO_DEFINITION_FOR_EXTRACTOR = f"{SCENARIO} represents a user interface (UI)-based testing scenario, providing a sequence of steps. These steps encompass both actions to be executed and expected outcomes to verify."

    SCENARIO_EXTRACTOR_INSTANCES = [
        {
            f"{BUG_ID}": 1684459,
            f"{INPUT}": {
                f"{SUMMARY}": "The Personalize button's clicked and hover states are reversed",
                f"{DESCRIPTION}": """**[Affected versions]:**
    - Firefox Nightly 86.0a1, BuildID 20201228205313
    - Firefox Beta 85.0b4, BuildID 20201220193140

    **[Affected Platforms]:**
    - Windows 10
    - macOS 10.15
    - Linux MX 4.19

    **[Prerequisites]:**
    - Have a new Firefox profile.
    - Have the `browser.newtabpage.activity-stream.newNewtabExperience.enabled` pref set to `true`.

    **[Steps to reproduce]:**
    1. Open the browser with the profile from prerequisites and open a new tab.
    2. Hover the "Personalize" button and observe the bahavior.
    3. Click and hold the "Personalize" button and observe the behavior.

    **[Expected results]:**
    - Light theme:
      - Step 2: The button has a dark gray hover effect.
      - Step 3: The button becomes darker.
    - Dark theme:
      - Step 2: The button has a light gray hover effect.
      - Step 3: The button becomes even lighter.

    **[Actual results]:**
    - Light theme:
      - Step 2: The button has a dark gray hover effect.
      - Step 3: The button becomes lighter.
    - Dark theme:
      - Step 2: The button has a light gray hover effect.
      - Step 3: The button becomes darker.

    **[Additional notes]:**
    - The issue is also reproducible on the Light theme, but it's much more noticeable on Dark theme.
    - Attached a screen recording of the issue.""",
            },
            f"{OUTPUT}": {
                # f"{CHAIN_OF_THOUGHTS}": None,
                f"{SCENARIOS}": [
                    {
                        f"{SUMMARY}": "Verify that the 'Personalize' button's hover and clicked states display the correct colors on Light Theme",
                        f"{STEPS}": [
                            "Open the browser with a new Firefox profile.",
                            "Set 'browser.newtabpage.activity-stream.newNewtabExperience.enabled' pref to 'true'.",
                            "Set the browser on Light Theme.",
                            "Open a new tab in the browser.",
                            "Hover the \"Personalize\" button and observe the button should have a dark gray hover effect.",
                            "Click and hold the \"Personalize\" button and observe the button should become darker, not lighter."],
                    },
                    {
                        f"{SUMMARY}": "Verify that the 'Personalize' button's hover and clicked states display the correct colors on Dark Theme",
                        f"{STEPS}": [
                            "Open the browser with a new Firefox profile.",
                            "Set 'browser.newtabpage.activity-stream.newNewtabExperience.enabled' pref to 'true'.",
                            "Set the browser on Dark Theme.",
                            "Open a new tab in the browser.",
                            "Hover the \"Personalize\" button and observe the button should have a light gray hover effect.",
                            "Click and hold the \"Personalize\" button and observe the button should become even lighter, not darker."],
                    },
                ],
            }
        },
        {
            f"{BUG_ID}": 1554038,
            f"{INPUT}": {
                f"{SUMMARY}": "Quantumbar intermittently stops working (TypeError: result is undefined UrlbarInput.jsm:437:9)",
                f"{DESCRIPTION}": """User Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:68.0) Gecko/20100101 Firefox/68.0

    Actual results:

    Since upgrading to v68 beta with Quantumbar enabled, the address bar will intermittently stop working (maybe 1 out of 20 times?). What happens is as follows:

    1. I'll type something in the address bar, and press tab to move down to a result.
    2. Pressing enter will do nothing - the result will still be highlighted and will not load.
    3. Every time I press enter, the following error will appear in the browser console:
    TypeError: result is undefined          UrlbarInput.jsm:437:9
    4. If I close the address bar and re-open it, it will start working again.

    I can't make this happen reliably, and there doesn't seem to be anything else that's obviously different between when it works and when it doesn't; if there's something you want me to test to narrow this down further, let me know and I'd be happy to try it.
    """},
            f"{OUTPUT}": {
                # f"{CHAIN_OF_THOUGHTS}": None,
                f"{SCENARIOS}": [
                    {
                        f"{SUMMARY}": "Verify that the Quantumbar responds correctly to user input and navigation commands with no errors",
                        f"{STEPS}": [
                            "Enable Quantumbar",
                            "Type something in the address bar.",
                            "Press tab to move down to a result.",
                            "Press enter and confirm that the selected result loads correctly.",
                            "Observe no errors in the browser console after pressing enter.",
                        ],
                    },
                ]}
        },
    ]

    STEP_SPLITTER_INSTANCES = [
        {
            f"{INPUT}": {f"{STEPS}": [
                "Open the browser with a new Firefox profile.",
                "Set 'browser.newtabpage.activity-stream.newNewtabExperience.enabled' pref to 'true'.",
                "Set the browser on Light Theme.",
                "Open a new tab in the browser.",
                "Hover the \"Personalize\" button and observe the button should have a dark gray hover effect.",
                "Click and hold the \"Personalize\" button and observe the button should become darker, not lighter."]},
            f"{OUTPUT}": {
                f"{STEPS}": [
                    {f"{STEP}": "Open the browser with a new Firefox profile.", f"{STEP_TYPE}": f"{STEP_TYPE_ACTION}"},
                    {f"{STEP}": "Set 'browser.newtabpage.activity-stream.newNewtabExperience.enabled' pref to 'true'.",
                     f"{STEP_TYPE}": f"{STEP_TYPE_ACTION}"},
                    {f"{STEP}": "Set the browser on Light Theme.", f"{STEP_TYPE}": f"{STEP_TYPE_ACTION}"},
                    {f"{STEP}": "Open a new tab in the browser.", f"{STEP_TYPE}": f"{STEP_TYPE_ACTION}"},
                    {f"{STEP}": "Hover the \"Personalize\" button.", f"{STEP_TYPE}": f"{STEP_TYPE_ACTION}"},
                    {f"{STEP}": "Observe the button should have a dark gray hover effect.",
                     f"{STEP_TYPE}": f"{STEP_TYPE_CHECK}"},
                    {f"{STEP}": "Click and hold the \"Personalize\" button.", f"{STEP_TYPE}": f"{STEP_TYPE_ACTION}"},
                    {f"{STEP}": "Observe the button should become darker, not lighter.",
                     f"{STEP_TYPE}": f"{STEP_TYPE_CHECK}"},
                ],
            }
        },
        {
            f"{INPUT}": {
                f"{STEPS}": [
                    "Enable Quantumbar",
                    "Type something in the address bar.",
                    "Press tab to move down to a result.",
                    "Press enter and confirm that the selected result loads correctly.",
                    "Observe no errors in the browser console after pressing enter.",
                ], },
            f"{OUTPUT}": {
                f"{STEPS}": [
                    {f"{STEP}": "Enable Quantumbar.", f"{STEP_TYPE}": f"{STEP_TYPE_ACTION}"},
                    {f"{STEP}": "Type something in the address bar.", f"{STEP_TYPE}": f"{STEP_TYPE_ACTION}"},
                    {f"{STEP}": "Press tab to move down to a result.", f"{STEP_TYPE}": f"{STEP_TYPE_ACTION}"},
                    {f"{STEP}": "Press enter.", f"{STEP_TYPE}": f"{STEP_TYPE_ACTION}"},
                    {f"{STEP}": "Confirm that the selected result loads correctly.",
                     f"{STEP_TYPE}": f"{STEP_TYPE_CHECK}"},
                    {f"{STEP}": "Observe no errors in the browser console after pressing enter.",
                     f"{STEP_TYPE}": f"{STEP_TYPE_CHECK}"},
                ],
            }
        }
    ]

    SCENARIO_EXTRACTION_JSON_FORMAT = '{' \
                                      f'"{SUMMARY}": "",' \
                                      f'"{STEPS}": ["",],' \
                                      '}'

    SCENARIOS_EXTRACTION_JSON_FORMAT = '{' \
                                       f'{SCENARIOS}":[{SCENARIO_EXTRACTION_JSON_FORMAT}, ]' \
                                       '}'
    SCENARIOS_EXTRACTION_COTS_JSON_FORMAT = "{" \
                                            f'"{CHAIN_OF_THOUGHTS}": "", ' \
                                            f'"{SCENARIOS_EXTRACTION_JSON_FORMAT},' \
                                            "}\n"

    STEP_WITH_TYPE_JSON_FORMAT = '{' \
                                 f'{STEP}: "", {STEP_TYPE}: ""' \
                                 '}'

    STEPS_SPLITTER_JSON_FORMAT = '{' \
                                 f'{STEPS}":[{STEP_WITH_TYPE_JSON_FORMAT}, ]' \
                                 '}'

    NON_OPERATION = 'NON_OPERATION'

    STEP_SPLITTER_INSTANCES_WITH_TYPE = [
        {
            "bug_id": 1556965,
            STEPS_TO_REPRODUCE: ["- Launch Firefox and enable the prefs",
                                 "- Go to about:logins",
                                 "- Create new entries until the list becomes scrollable",
                                 "- Scroll the entries list and observe the Header"],
            "output": {STEPS: [
                {STEP: "Launch Firefox", STEP_TYPE: OPERATION},
                {STEP: "Enable the prefs", STEP_TYPE: OPERATION},
                {STEP: "Go to 'about:logins'", STEP_TYPE: OPERATION},
                {STEP: "Create new entries until the list becomes scrollable", STEP_TYPE: OPERATION},
                {STEP: "Scroll the entries list", STEP_TYPE: OPERATION},
                {STEP: "Observe the Header", STEP_TYPE: NON_OPERATION},
            ]}
        },
        {
            "bug_id": 1730692,
            STEPS_TO_REPRODUCE: ["1. Restart the browser after setting prerequisite preferences.",
                                 "2. Dismiss the Make Firefox default message if it is displayed to trigger the "
                                 "Suggestions modal.",
                                 "3. Open System Settings > Ease of Access > Display.",
                                 "4. Set the “Make text bigger” slider to a larger value (e.g. 135% ).",
                                 "5. Observe the modal."],
            "output": {STEPS: [
                {STEP: "Set prerequisite preferences.", STEP_TYPE: OPERATION},
                {STEP: "Restart the browser.", STEP_TYPE: OPERATION},
                {STEP: "Dismiss the Make Firefox default message if it is displayed to trigger the Suggestions modal.",
                 STEP_TYPE: OPERATION},
                {STEP: "Open 'System Settings'.", STEP_TYPE: OPERATION},
                {STEP: "Select 'Ease of Access'.", STEP_TYPE: OPERATION},
                {STEP: "Click on 'Display' option.", STEP_TYPE: OPERATION},
                {STEP: "Set the 'Make text bigger' slider to a larger value (e.g. 135% ).",
                 STEP_TYPE: OPERATION},
                {STEP: "Observe the modal.", STEP_TYPE: NON_OPERATION},
            ]}
        },
    ]

    SEC_SPLITTER_INSTANCES = [
        {
            # only steps to reproduce
            "bug_id": 1537640,
            "summary": "Firefox adds zeros to http://192. making it really obnoxious to get to internal addresses",
            "description": """User Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0

Steps to reproduce:

My firefox upgraded to release 66 tonight. It immediately exhibited a new behavior that is really annoying.  If I go to the URL bar and type:

http://192.
or
https://192.

Firefox will immediately substitute 0.0.0 after the "." into the URL bar.

So to get to internal addresses like 192.168.1.1 I have to manually delete these values.

This did not happen prior to Firefox 66.""",
            "output": {
                "PRECONDITIONS": [],
                "STEPS_TO_REPRODUCE": [
                    "Go to the URL bar",
                    "Type 'http://192.' or 'https://192.'"
                ],
                "EXPECTED_RESULTS": [
                    "URL bar should retain the typed value without any substitution or modification"
                ],
                "ACTUAL_RESULTS": [
                    "After typing 'http://192.' or 'https://192.' in the URL bar, "
                    "Firefox automatically substitutes '0.0.0' after the '. "
                    "So to get to internal addresses like 192.168.1.1, I have to manually delete these values."
                ],
                "NOTES": [
                    "This behavior started after upgrading to Firefox 66"
                ],
                "AFFECTED_VERSIONS": [
                    "Firefox version 66"
                ],
                "AFFECTED_PLATFORMS": [
                    "Windows NT 10.0"
                ],
                "OTHERS": [
                    "User Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0"
                ]
            }
        },
        {
            # only steps to reproduce, preconditions in S2R, no expected results
            "bug_id": 1578873,
            "summary": "Tabbing gets stuck on 'Create New Login' when there are zero saved logins.",
            "description": """Created attachment 9090502
focusIsStuckOnButton.png

Tabbing gets stuck on the "Create New Login" button on the 9/4 build of Nightly when there are zero saved logins. The "Lockwise Support" link can only be accessed via keyboard by tabbing backwards through the page elements.

Steps to reproduce:
- With no previously saved logins, open `about:logins` in 9/4 build of Nightly and begin tabbing through page elements.
""",
            "output": {
                "PRECONDITIONS": [
                    "No previously saved logins",
                ],
                "STEPS_TO_REPRODUCE": [
                    "Open about:logins",
                    "Start tabbing through page elements"
                ],
                "EXPECTED_RESULTS": [
                    "Tabbing should proceed smoothly through all page elements"
                ],
                "ACTUAL_RESULTS": [
                    "Tabbing gets stuck on the \"Create New Login\" button when there are zero saved logins",
                    "The \"Lockwise Support\" link can only be accessed via keyboard by tabbing backwards"
                ],
                "NOTES": [],
                "AFFECTED_VERSIONS": [
                    "Nightly build on 9/4"
                ],
                "AFFECTED_PLATFORMS": [
                ],
                "OTHERS": [
                    "Attachment: focusIsStuckOnButton.png"
                ]
            }
        },
        {
            # all in one paragraph
            "bug_id": 1552289,
            "summary": """"Search only" view doesn't work for DiscoveryStream""",
            "description": """Not sure if this is intended, but even if both Top Sites and Pocket are off the special firefox logo search-only view is not shown in DS.

This is because the search-only view is expecting highlights to be off, but that section doesn't exist in the settings for discovery stream.
""",
            "output": {
                "PRECONDITIONS": [
                    "Top Sites and Pocket are both turned off",
                ],
                "STEPS_TO_REPRODUCE": [
                    "Open DiscoveryStream",
                    "Check if the search-only view is shown"
                ],
                "EXPECTED_RESULTS": [
                    "The search-only view should be shown"
                ],
                "ACTUAL_RESULTS": [
                    "The search-only view is not shown"
                ],
                "NOTES": [
                    "The search-only view is expecting highlights to be off, but that section doesn't exist in the settings for discovery stream."],
                "AFFECTED_VERSIONS": [
                ],
                "AFFECTED_PLATFORMS": [
                ],
                "OTHERS": [
                ]
            }
        },

    ]

    UNIQUE_BUG_NO = 'UNIQUE_BUG_NO'
    DUPLICATE_BUGS = 'DUPLICATE_BUGS'
    DEDUPLICATOR_OUTPUT = 'DEDUPLICATOR_OUTPUT'

    DEDUPLICATOR_FORMAT = {
        DEDUPLICATOR_OUTPUT:
            [
                {
                    UNIQUE_BUG_NO: "",
                    DUPLICATE_BUGS: [
                    ]
                },
            ]
    }

    VALID_ISSUES = "VALID_ISSUES"
    INVALID_ISSUES = "INVALID_ISSUES"
    CLASSIFIER_RESULT = 'CLASSIFIER_RESULT'
    # CLASSIFIER_FORMAT = {
    #     VALID_ISSUES: [],
    #     INVALID_ISSUES: []
    # }
    CLASSIFIER_FORMAT = {
        CLASSIFIER_RESULT: "True or False",
    }

    TYPE_ENHANCEMENT = 'ENHANCEMENT'
    TYPE_DEFECT = 'DEFECT'

    BUG_VALIDITY = 'VALIDITY'
    VALID = 'VALID'
    INVALID = 'INVALID'

    VALIDITY_REASON = 'VALIDITY_REASON'
    VALID_OPTION_1 = 'Oracle from creative thinking'
    VALID_OPTION_2 = 'Oracle from KG'

    # VALIDITY_REASON = 'INVALID_REASON'
    INVALID_OPTION_1 = 'Response delay or incomplete loading'
    INVALID_OPTION_2 = 'Dynamic changes not captured'
    INVALID_OPTION_3 = 'Player location error'
    INVALID_OPTION_4 = 'Player limited operation type'
    INVALID_OPTION_5 = 'Hallucination'
    INVALID_OPTION_6 = 'Misunderstood or overlooked'
    INVALID_OPTION_7 = 'Unexecuted execution plan'
    INVALID_OPTION_8 = 'Unreasonable or unnecessary'

    PLAN_CURRENT_STEP_VALIDITY = 'PLAN_CURRENT_STEP_VALIDITY'
    PLAN_SUB_STEPS_VALIDITY = 'PLAN_SUB_STEPS_VALIDITY'

    PLAY_STEP_PARSE_VALIDITY = 'PLAY_STEP_PARSE_VALIDITY'
    PLAY_STEP_PARSE_INVALID_OPTION_1 = 'INVALID_ACTION'
    PLAY_STEP_PARSE_INVALID_OPTION_2 = 'INVALID_ELEMENT'
    PLAY_STEP_PARSE_INVALID_OPTION_3 = 'INVALID_INPUT'
    PLAY_STEP_PARSE_INVALIDITY_REASON = 'PLAY_STEP_PARSE_INVALIDITY_REASON'
    PLAY_ELEMENT_LOCATION_VALIDITY = 'PLAY_ELEMENT_LOCATION_VALIDITY'
