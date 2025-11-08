using System;
using System.Windows.Forms;
using System.Drawing;

namespace AirplaneSolidWorksAddin
{
    public partial class TaskpaneControl : UserControl
    {
        private AirplaneAddin _addin;
        private TextBox _promptTextBox;
        private Button _generateButton;
        private ListBox _examplesListBox;

        public TaskpaneControl(AirplaneAddin addin)
        {
            _addin = addin;
            InitializeComponent();
        }

        private void InitializeComponent()
        {
            this.SuspendLayout();

            // Title
            Label titleLabel = new Label
            {
                Text = "AI Airplane Generator",
                Font = new Font("Segoe UI", 12, FontStyle.Bold),
                Location = new Point(10, 10),
                Size = new Size(280, 30),
                TextAlign = ContentAlignment.MiddleLeft
            };
            this.Controls.Add(titleLabel);

            // Prompt label
            Label promptLabel = new Label
            {
                Text = "Describe your airplane:",
                Location = new Point(10, 50),
                Size = new Size(280, 20)
            };
            this.Controls.Add(promptLabel);

            // Prompt text box
            _promptTextBox = new TextBox
            {
                Location = new Point(10, 75),
                Size = new Size(280, 80),
                Multiline = true,
                ScrollBars = ScrollBars.Vertical,
                Text = "Fighter jet with swept wings, 15m wingspan"
            };
            this.Controls.Add(_promptTextBox);

            // Generate button
            _generateButton = new Button
            {
                Text = "Generate Airplane",
                Location = new Point(10, 165),
                Size = new Size(280, 35),
                BackColor = Color.FromArgb(0, 120, 215),
                ForeColor = Color.White,
                FlatStyle = FlatStyle.Flat,
                Font = new Font("Segoe UI", 10, FontStyle.Bold)
            };
            _generateButton.Click += GenerateButton_Click;
            this.Controls.Add(_generateButton);

            // Examples label
            Label examplesLabel = new Label
            {
                Text = "Example prompts:",
                Location = new Point(10, 210),
                Size = new Size(280, 20),
                Font = new Font("Segoe UI", 9, FontStyle.Bold)
            };
            this.Controls.Add(examplesLabel);

            // Examples list
            _examplesListBox = new ListBox
            {
                Location = new Point(10, 235),
                Size = new Size(280, 200)
            };
            _examplesListBox.Items.AddRange(new object[]
            {
                "Fighter jet with delta wings",
                "Commercial airliner, 60m wingspan",
                "Small propeller plane, high wings",
                "Stealth bomber, flying wing design",
                "Business jet, 12m wingspan",
                "Vintage biplane with struts",
                "Cargo plane with high tail"
            });
            _examplesListBox.DoubleClick += ExamplesList_DoubleClick;
            this.Controls.Add(_examplesListBox);

            // Help text
            Label helpLabel = new Label
            {
                Text = "Tip: Double-click an example to use it",
                Location = new Point(10, 445),
                Size = new Size(280, 40),
                ForeColor = Color.Gray,
                Font = new Font("Segoe UI", 8)
            };
            this.Controls.Add(helpLabel);

            // Control settings
            this.BackColor = Color.White;
            this.Size = new Size(300, 500);
            this.ResumeLayout(false);
        }

        private async void GenerateButton_Click(object? sender, EventArgs e)
        {
            string prompt = _promptTextBox.Text.Trim();
            if (string.IsNullOrEmpty(prompt))
            {
                MessageBox.Show("Please enter a description", "Input Required",
                    MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return;
            }

            _addin.GenerateAirplane();
        }

        private void ExamplesList_DoubleClick(object? sender, EventArgs e)
        {
            if (_examplesListBox.SelectedItem != null)
            {
                _promptTextBox.Text = _examplesListBox.SelectedItem.ToString();
            }
        }
    }
}
