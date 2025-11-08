using System;
using System.Runtime.InteropServices;
using System.Windows.Forms;
using SolidWorks.Interop.sldworks;
using SolidWorks.Interop.swconst;
using SolidWorks.Interop.swpublished;
using SolidWorksTools;
using SolidWorksTools.File;

namespace AirplaneSolidWorksAddin
{
    [Guid("8B5E9A2C-4F3D-4E1A-9B2C-7D8E6F5A4B3C")]
    [ComVisible(true)]
    [SwAddin(
        Description = "AI-powered airplane 3D model generator",
        Title = "Airplane Generator",
        LoadAtStartup = true
    )]
    public class AirplaneAddin : ISwAddin
    {
        private ISldWorks? _swApp;
        private int _addinId;
        private TaskpaneView? _taskpaneView;
        private TaskpaneControl? _taskpaneControl;
        private LLMService? _llmService;

        // COM Registration
        [ComRegisterFunction]
        public static void RegisterFunction(Type t)
        {
            try
            {
                Microsoft.Win32.RegistryKey key =
                    Microsoft.Win32.Registry.LocalMachine.CreateSubKey(
                        @"SOFTWARE\SolidWorks\Addins\{8B5E9A2C-4F3D-4E1A-9B2C-7D8E6F5A4B3C}");

                key.SetValue(null, 0);
                key.SetValue("Description", "AI-powered airplane generator");
                key.SetValue("Title", "Airplane Generator");
                key.Close();
            }
            catch (Exception ex)
            {
                MessageBox.Show("Error during registration: " + ex.Message);
            }
        }

        [ComUnregisterFunction]
        public static void UnregisterFunction(Type t)
        {
            try
            {
                Microsoft.Win32.Registry.LocalMachine.DeleteSubKey(
                    @"SOFTWARE\SolidWorks\Addins\{8B5E9A2C-4F3D-4E1A-9B2C-7D8E6F5A4B3C}");
            }
            catch { }
        }

        // ISwAddin Implementation
        public bool ConnectToSW(object ThisSW, int cookie)
        {
            _swApp = (ISldWorks)ThisSW;
            _addinId = cookie;

            // Load .env file
            EnvLoader.Load();

            // Initialize LLM service
            string? apiKey = EnvLoader.GetValue("OPENAI_API_KEY");
            string model = EnvLoader.GetValue("OPENAI_MODEL", "gpt-4");
            string tempStr = EnvLoader.GetValue("OPENAI_TEMPERATURE", "0.3");
            float temperature = float.TryParse(tempStr, out float temp) ? temp : 0.3f;

            if (!string.IsNullOrEmpty(apiKey))
            {
                _llmService = new LLMService(apiKey, model, temperature);
            }

            // Add menu and toolbar
            if (!SetupUI())
            {
                return false;
            }

            // Create task pane
            CreateTaskPane();

            return true;
        }

        public bool DisconnectFromSW()
        {
            RemoveUI();
            return true;
        }

        private bool SetupUI()
        {
            try
            {
                // Get command manager
                ICommandManager cmdMgr = _swApp!.GetCommandManager(_addinId);

                // Create command group
                ICommandGroup cmdGroup = cmdMgr.CreateCommandGroup2(
                    1,
                    "Airplane Generator",
                    "AI-powered airplane generator",
                    "",
                    -1,
                    false,
                    ref _);

                // Add Generate command
                int cmdIndex = cmdGroup.AddCommandItem2(
                    "Generate Airplane",
                    -1,
                    "Generate airplane from text prompt",
                    "Generate Airplane",
                    0,
                    nameof(GenerateAirplane),
                    "",
                    1,
                    (int)swCommandItemType_e.swMenuItem);

                // Add Show Panel command
                cmdGroup.AddCommandItem2(
                    "Show Panel",
                    -1,
                    "Show airplane generator panel",
                    "Show Panel",
                    0,
                    nameof(ShowTaskPane),
                    "",
                    2,
                    (int)swCommandItemType_e.swMenuItem);

                cmdGroup.HasToolbar = true;
                cmdGroup.HasMenu = true;
                cmdGroup.Activate();

                return true;
            }
            catch (Exception ex)
            {
                MessageBox.Show("Error setting up UI: " + ex.Message);
                return false;
            }
        }

        private void RemoveUI()
        {
            if (_taskpaneView != null)
            {
                _taskpaneView.DeleteView();
            }
        }

        private void CreateTaskPane()
        {
            try
            {
                _taskpaneControl = new TaskpaneControl(this);

                _taskpaneView = _swApp!.CreateTaskpaneView2(
                    _taskpaneControl,
                    "Airplane Generator");

                _taskpaneView.DisplayWhenActive = true;
            }
            catch (Exception ex)
            {
                MessageBox.Show("Error creating task pane: " + ex.Message);
            }
        }

        public async void GenerateAirplane()
        {
            if (_swApp == null) return;

            try
            {
                // Get prompt from user
                string prompt = PromptForInput("Enter airplane description:",
                    "Fighter jet with swept wings, 15m wingspan");

                if (string.IsNullOrEmpty(prompt))
                    return;

                // Check API key
                if (_llmService == null)
                {
                    MessageBox.Show(
                        "OPENAI_API_KEY not configured!\n\n" +
                        "Please set it in the .env file:\n" +
                        "OPENAI_API_KEY=sk-proj-your-key-here\n\n" +
                        "The .env file should be in the add-in directory.",
                        "Configuration Error",
                        MessageBoxButtons.OK,
                        MessageBoxIcon.Error);
                    return;
                }

                // Show progress
                var progressForm = new Form
                {
                    Text = "Generating Airplane",
                    Width = 300,
                    Height = 100,
                    FormBorderStyle = FormBorderStyle.FixedDialog,
                    StartPosition = FormStartPosition.CenterScreen
                };
                var label = new Label
                {
                    Text = "Analyzing prompt with AI...",
                    Dock = DockStyle.Fill,
                    TextAlign = System.Drawing.ContentAlignment.MiddleCenter
                };
                progressForm.Controls.Add(label);
                progressForm.Show();

                // Parse prompt with AI
                var parameters = await _llmService.ParseAirplanePrompt(prompt);

                label.Text = $"Generating 3D model...\n{parameters.Type}, {parameters.Wingspan}m wingspan";
                Application.DoEvents();

                // Generate the airplane
                var generator = new AirplaneGenerator(_swApp, parameters);
                bool success = generator.Generate();

                progressForm.Close();

                if (success)
                {
                    MessageBox.Show(
                        "Airplane generated successfully!\n\n" +
                        "You can now:\n" +
                        "• Modify the model\n" +
                        "• Export to STL (File > Save As > STL)\n" +
                        "• Run simulations",
                        "Success",
                        MessageBoxButtons.OK,
                        MessageBoxIcon.Information);
                }
                else
                {
                    MessageBox.Show("Failed to generate airplane", "Error",
                        MessageBoxButtons.OK, MessageBoxIcon.Error);
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Error: {ex.Message}\n\n{ex.StackTrace}",
                    "Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }

        public void ShowTaskPane()
        {
            if (_taskpaneView != null)
            {
                _taskpaneView.DisplayWhenActive = true;
            }
        }

        private string PromptForInput(string prompt, string defaultValue)
        {
            Form promptForm = new Form()
            {
                Width = 500,
                Height = 200,
                FormBorderStyle = FormBorderStyle.FixedDialog,
                Text = "Airplane Generator",
                StartPosition = FormStartPosition.CenterScreen
            };

            Label textLabel = new Label() { Left = 20, Top = 20, Width = 450, Text = prompt };
            TextBox textBox = new TextBox() { Left = 20, Top = 50, Width = 450, Height = 60, Multiline = true, Text = defaultValue };
            Button confirmation = new Button() { Text = "Generate", Left = 300, Width = 80, Top = 120, DialogResult = DialogResult.OK };
            Button cancel = new Button() { Text = "Cancel", Left = 390, Width = 80, Top = 120, DialogResult = DialogResult.Cancel };

            confirmation.Click += (sender, e) => { promptForm.Close(); };
            cancel.Click += (sender, e) => { promptForm.Close(); };

            promptForm.Controls.Add(textLabel);
            promptForm.Controls.Add(textBox);
            promptForm.Controls.Add(confirmation);
            promptForm.Controls.Add(cancel);
            promptForm.AcceptButton = confirmation;
            promptForm.CancelButton = cancel;

            return promptForm.ShowDialog() == DialogResult.OK ? textBox.Text : "";
        }

        public ISldWorks? SwApp => _swApp;
        public LLMService? LlmService => _llmService;
    }
}
