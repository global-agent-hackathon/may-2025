# SDET-GENIE: AI-AGENTS in QA Automation @AGNO @Browser-use

![image](https://raw.githubusercontent.com/BharathLakkoju/global-agent-hackathon-may-2025/refs/heads/main/.assets/agno_architecture.png)

## 🚀 Project Overview

SDET-GENIE is a cutting-edge, AI-powered Quality Assurance (QA) automation framework that revolutionizes the software testing process. Leveraging a suite of specialized AI agents, SDET-GENIE transforms rough user stories into comprehensive, executable test automation code through a seamless end-to-end process.

The framework integrates five powerful AI agents working in sequence:

1. **User Story Enhancement Agent** - Transforms rough ideas into detailed JIRA-style user stories
2. **Manual Test Case Agent** - Converts enhanced user stories into comprehensive test cases
3. **Gherkin Scenario Agent** - Transforms test cases into structured Gherkin feature files
4. **Browser Agent** - Executes Gherkin scenarios in real browsers and captures interaction data
5. **Code Generation Agent** - Produces ready-to-run automation code in multiple frameworks

## 🌟 Key Features

### 1. User Story Enhancement Agent

- Transforms rough, incomplete user stories into detailed, valuable JIRA-style user stories
- Ensures proper WHO, WHAT, and WHY structure
- Adds comprehensive acceptance criteria and implementation notes
- Creates appropriately sized stories that can be completed in a single sprint

### 2. Manual Test Case Agent

- Converts user stories and acceptance criteria into comprehensive manual test cases
- Generates positive, negative, edge, and boundary test scenarios
- Creates detailed test steps with expected results
- Produces industry-standard test documentation

### 3. Gherkin Scenario Agent

- Transforms manual test cases into well-structured Gherkin scenarios
- Creates human-readable feature files with proper Given/When/Then syntax
- Supports scenario outlines for data-driven testing
- Adds appropriate tags for test organization and filtering

### 4. Intelligent Browser Agent

- Automated browser interaction and test execution
- Dynamic element identification and mapping
- Comprehensive DOM detail capture
- Robust element selector generation

### 5. Code Generation Agent

- Produces production-ready automation code from Gherkin scenarios
- Supports multiple testing frameworks (Selenium, Playwright, Cypress, etc.)
- Generates clean, well-structured, and maintainable code
- Includes all necessary imports, dependencies, and helper functions

## 🔧 Technology Stack

- Python
- AI Models (Google Gemini 2.0 Flash)
- Selenium/Playwright
- Gherkin/Cucumber
- Browser Automation Technologies

## 📦 Installation - Quick start

install playwright:

```shell
playwright install
```

```bash

git clone https://github.com/WaiGenie/SDET-GENIE.git

cd SDET-GENIE

python -m venv .venv

.venv\Scripts\activate

pip install-requirements.txt

Create .env file
Place your GOOGLE_API_KEY=AIzaXXXXXXXXXXXXXX

streamlit run app.py

```

## 🖥️ Quick Start

1. Prepare your user story
2. Run the AI agents
3. Generate and execute automated tests

## 🤝 Contributing

We're excited to welcome contributors to SDET-GENIE! Whether you're fixing bugs, improving documentation, or adding new features, your contributions are highly valued.

### 💡 Why Contribute?

- Gain experience with cutting-edge AI and test automation technologies
- Join a growing community of QA automation enthusiasts
- Help shape the future of AI-powered testing
- Get your name featured in our contributors list
- Learn best practices in test automation

### 🚀 Getting Started with Contributions

```
2. Create a new branch (`git checkout -b feature/your-feature-name`)
3. Make your changes
4. Run tests
5. Commit your changes
6. Push to your fork
7. Open a Pull Request
```

## 🔍 Areas for Contribution

- Bug fixes
- Documentation improvements
- New test automation framework support
- Performance optimizations
- Cloud browser provider integrations
- UI/UX improvements
- Test coverage enhancements

## 📄 License

This project is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0)

### License Highlights

✔️ Personal and educational use allowed

✔️ Code modification permitted

✔️ Copyright and license notices must be preserved

✔️ Source code must be disclosed when distributing

✔️ Changes must be released under the same license

❌ No commercial use without explicit permission

❌ No warranty provided

For full license details, see the [LICENSE](LICENSE) file or visit [GNU AGPL-3.0](https://www.gnu.org/licenses/agpl-3.0.en.html)

## 🤔 Questions or Need Help?

- Open a GitHub Discussion
- Check existing issues
- Join our community Discord - https://discord.gg/QqF68r39

## 📚 Blog Post

Read our in-depth article: [From User Stories to Automated Tests: The Future of QA Automation using AI Agents](https://medium.com/@honeyricky1m3/from-user-stories-to-automated-tests-the-future-of-qa-automation-using-ai-agents-cfe7fe878954)

Demo - https://youtu.be/z0fSNoUZTzw?si=xrfbDsGWlnTJzcYK

## 🌈 Acknowledgments

- Inspired by the challenges in modern software quality assurance
- Powered by cutting-edge AI technologies

## How it works:

```
1. Entrypoint: User provides a rough user story about what to test in the website.

2. User Story Enhancement:
   - The User Story Enhancement Agent transforms the rough user story into a detailed, JIRA-style user story
   - Adds proper structure (WHO, WHAT, WHY), acceptance criteria, and implementation notes

3. Manual Test Case Generation:
   - The Manual Test Case Agent converts the enhanced user story into comprehensive test cases
   - Generates positive, negative, edge, and boundary test scenarios with detailed steps

4. Gherkin Scenario Generation:
   - The Gherkin Agent transforms manual test cases into well-structured Gherkin scenarios
   - Creates feature files with proper Given/When/Then syntax and scenario outlines

5. Browser Automation:
   - The Browser Agent executes each Gherkin scenario in a real browser
   - Custom actions registered:
     -> "Get XPath of element using index"
     -> "Get element property"
     -> "Perform element action"
   - Executes and collects results:
     history = await browser_agent.run()

6. Data Collection from Browser:
   - Collects XPaths, actions, and extracted content from browser interactions
   - Saves combined history to session state:
     st.session_state.history = {
         "urls": history.urls(),
         "action_names": history.action_names(),
         "detailed_actions": all_actions,
         "element_xpaths": element_xpath_map,
         "extracted_content": all_extracted_content,
         "errors": history.errors(),
         "model_actions": history.model_actions(),
         "execution_date": st.session_state.get("execution_date", "Unknown")
     }

7. Test Automation Code Generation:
   - The Code Generation Agent produces ready-to-execute test automation code
   - Uses Gherkin scenarios and browser interaction data to generate code
   - Supports multiple frameworks (Selenium, Playwright, Cypress, etc.)
   - automation_code = generator_function(
         generated_steps,  # Generated Gherkin scenarios
         history           # Browser interaction data
     )
```

**Made with ❤️ by the WaiGenie Team**
