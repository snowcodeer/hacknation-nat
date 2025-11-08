using System;
using System.Text.Json;
using System.Threading.Tasks;
using OpenAI.Chat;

namespace AirplaneSolidWorksAddin
{
    public class AirplaneParameters
    {
        public string Type { get; set; } = "generic";
        public double Wingspan { get; set; } = 10.0;
        public double FuselageLength { get; set; } = 8.0;
        public double FuselageRadius { get; set; } = 0.6;
        public double TailHeight { get; set; } = 2.5;
        public string WingType { get; set; } = "swept";
        public int EngineCount { get; set; } = 2;
        public bool HasCanopy { get; set; } = true;
        public double NoseLength { get; set; } = 2.0;
        public double WingSweepAngle { get; set; } = 25.0; // degrees
    }

    public class LLMService
    {
        private readonly ChatClient _client;
        private readonly string _model;
        private readonly float _temperature;

        public LLMService(string apiKey, string model = "gpt-4", float temperature = 0.3f)
        {
            _client = new ChatClient(model, apiKey);
            _model = model;
            _temperature = temperature;
        }

        public async Task<AirplaneParameters> ParseAirplanePrompt(string prompt)
        {
            var systemPrompt = @"You are an expert aerospace engineer helping to extract airplane design parameters from text descriptions.
Analyze the user's description and extract specific numeric parameters for 3D modeling in SolidWorks.

Return ONLY a valid JSON object with these fields:
{
  ""type"": ""fighter"" | ""commercial"" | ""propeller"" | ""glider"" | ""generic"",
  ""wingspan"": number (meters, typical: 10-60),
  ""fuselageLength"": number (meters, typical: 8-50),
  ""fuselageRadius"": number (meters, typical: 0.5-3),
  ""tailHeight"": number (meters, typical: 2-8),
  ""wingType"": ""swept"" | ""delta"" | ""straight"" | ""high"",
  ""engineCount"": number (0-4),
  ""hasCanopy"": boolean,
  ""noseLength"": number (meters, typical: 1-5),
  ""wingSweepAngle"": number (degrees, 0-45, default 25 for swept wings)
}

Use reasonable defaults based on airplane type if specifics aren't mentioned.
For commercial airliners: use larger dimensions, 4 engines
For fighters: swept or delta wings, 2 engines, smaller size
For propeller planes: straight wings, 0-1 engines, smaller size

Return ONLY the JSON object, no markdown code blocks or additional text.";

            try
            {
                var messages = new[]
                {
                    new SystemChatMessage(systemPrompt),
                    new UserChatMessage(prompt)
                };

                var completionOptions = new ChatCompletionOptions
                {
                    Temperature = _temperature,
                    MaxOutputTokenCount = 500
                };

                var completion = await _client.CompleteChatAsync(messages, completionOptions);
                string jsonResponse = completion.Value.Content[0].Text;

                // Clean up response if it has markdown code blocks
                jsonResponse = jsonResponse.Trim();
                if (jsonResponse.StartsWith("```json"))
                {
                    jsonResponse = jsonResponse.Substring(7);
                }
                if (jsonResponse.StartsWith("```"))
                {
                    jsonResponse = jsonResponse.Substring(3);
                }
                if (jsonResponse.EndsWith("```"))
                {
                    jsonResponse = jsonResponse.Substring(0, jsonResponse.Length - 3);
                }
                jsonResponse = jsonResponse.Trim();

                var result = JsonSerializer.Deserialize<AirplaneParameters>(jsonResponse,
                    new JsonSerializerOptions { PropertyNameCaseInsensitive = true });

                return result ?? GetDefaultParameters();
            }
            catch (Exception ex)
            {
                Console.WriteLine($"LLM parsing error: {ex.Message}");
                return GetDefaultParameters();
            }
        }

        private AirplaneParameters GetDefaultParameters()
        {
            return new AirplaneParameters
            {
                Type = "generic",
                Wingspan = 10.0,
                FuselageLength = 8.0,
                FuselageRadius = 0.6,
                TailHeight = 2.5,
                WingType = "swept",
                EngineCount = 2,
                HasCanopy = true,
                NoseLength = 2.0,
                WingSweepAngle = 25.0
            };
        }
    }
}
