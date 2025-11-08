using System;
using System.IO;
using System.Reflection;

namespace AirplaneSolidWorksAddin
{
    public static class EnvLoader
    {
        private static bool _loaded = false;

        public static void Load()
        {
            if (_loaded) return;

            try
            {
                // Get the directory where the DLL is located
                string assemblyLocation = Assembly.GetExecutingAssembly().Location;
                string assemblyDirectory = Path.GetDirectoryName(assemblyLocation);

                // Look for .env file in the same directory as the DLL
                string envPath = Path.Combine(assemblyDirectory, ".env");

                if (!File.Exists(envPath))
                {
                    // Try parent directory (during development)
                    envPath = Path.Combine(Directory.GetParent(assemblyDirectory).FullName, ".env");
                }

                if (!File.Exists(envPath))
                {
                    // Try going up more levels for development scenario
                    string projectRoot = assemblyDirectory;
                    for (int i = 0; i < 5; i++)
                    {
                        projectRoot = Directory.GetParent(projectRoot)?.FullName;
                        if (projectRoot == null) break;

                        envPath = Path.Combine(projectRoot, ".env");
                        if (File.Exists(envPath)) break;
                    }
                }

                if (File.Exists(envPath))
                {
                    DotNetEnv.Env.Load(envPath);
                    _loaded = true;
                }
            }
            catch (Exception ex)
            {
                // Silently fail - will fall back to environment variables
                Console.WriteLine($"Warning: Could not load .env file: {ex.Message}");
            }
        }

        public static string GetValue(string key, string defaultValue = "")
        {
            Load();

            // Try .env file first
            string value = Environment.GetEnvironmentVariable(key);

            if (string.IsNullOrEmpty(value))
            {
                value = defaultValue;
            }

            return value;
        }
    }
}
