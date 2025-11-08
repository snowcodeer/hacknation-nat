# Airplane Generator for SolidWorks - AI-Powered 3D Modeling

SolidWorks add-in that generates parametric 3D airplane models from natural language prompts using OpenAI GPT.

## Features

- **AI-Powered**: Describe airplanes in plain English, GPT extracts parameters
- **Parametric CAD**: True SolidWorks features, fully editable
- **STL Export Ready**: Direct export for 3D printing and manufacturing
- **Interactive UI**: Task pane with example prompts
- **Professional Grade**: Engineering-ready CAD models
- **.env Configuration**: Easy API key management

## Quick Start

### Prerequisites

- **Windows 10/11** (SolidWorks is Windows-only)
- **SolidWorks 2020+** (tested on 2024/2025)
- **Visual Studio 2022** with .NET desktop development
- **.NET Framework 4.8** (included with VS 2022)
- **OpenAI API key** ([get one here](https://platform.openai.com/api-keys))

### Installation (10 minutes)

1. **Set up API Key**:
   - Copy `.env.example` to `.env`
   - Edit `.env` and add your OpenAI API key:
     ```
     OPENAI_API_KEY=sk-proj-your-key-here
     OPENAI_MODEL=gpt-4
     OPENAI_TEMPERATURE=0.3
     ```

2. **Open in Visual Studio**:
   - Open `AirplaneSolidWorksAddin.sln`
   - Update SolidWorks path in `.csproj` if needed:
     ```xml
     <SolidWorksPath>C:\Program Files\SOLIDWORKS Corp\SOLIDWORKS</SolidWorksPath>
     ```

3. **Build**:
   - Set to **Debug** or **Release**
   - Build > Build Solution (F6)

4. **Copy .env to build output**:
   - Copy `.env` to `bin\Debug\net48\` (or `bin\Release\net48\`)
   - This ensures the add-in can find your API key

5. **Register Add-in**:
   - Right-click `Register.bat`
   - Select "Run as administrator"
   - Wait for success message

6. **Enable in SolidWorks**:
   - Open SolidWorks
   - Tools > Add-Ins
   - Check "Airplane Generator" (both columns)

## Usage

### Method 1: Task Pane (Recommended)

1. Click "Airplane Generator" in the task pane (right side)
2. Enter description or double-click an example
3. Click "Generate Airplane"
4. Wait 5-10 seconds for AI processing
5. Your airplane appears as a new part!

### Method 2: Toolbar Button

1. Click "Generate Airplane" button in toolbar
2. Enter description in popup
3. Click Generate

## Example Prompts

```
"Fighter jet with swept wings, 15 meter wingspan, twin engines"
"Commercial airliner, wide body, 60m wingspan, 4 engines"
"Small propeller plane with high wings"
"Stealth bomber with flying wing design, 25m wingspan"
"Business jet, sleek design, 12m wingspan"
"Vintage biplane with double wings and struts"
"Large cargo plane with high tail, 50m wingspan"
```

### GPT Models

Choose in `.env` file:
- **gpt-4**: Best quality, slower, more expensive
- **gpt-4-turbo**: Faster, good quality
- **gpt-3.5-turbo**: Fastest, cheapest, decent quality

### Parameter Details

GPT extracts:
- **Type**: fighter, commercial, propeller, glider
- **Wingspan**: meters (controls overall size)
- **Fuselage length & radius**: body dimensions
- **Wing type**: swept, delta, straight, high
- **Engine count**: 0-4
- **Tail height**: vertical stabilizer size
- **Canopy**: yes/no for cockpit dome

## Exporting to STL

1. Select the generated airplane features
2. File > Save As
3. Select file type: **STL (*.stl)**
4. Click "Options" to adjust resolution
5. Save

## Configuration (.env file)

Create a `.env` file in the add-in directory with:

```bash
# Required: Your OpenAI API key
OPENAI_API_KEY=sk-proj-your-key-here

# Optional: Model selection (default: gpt-4)
# Options: gpt-4, gpt-4-turbo, gpt-3.5-turbo
OPENAI_MODEL=gpt-4

# Optional: Temperature for AI responses (0.0-1.0)
# Lower = more consistent, Higher = more creative
OPENAI_TEMPERATURE=0.3
```

**Important**: The `.env` file must be copied to the build output directory:
- `bin\Debug\net48\.env` for Debug builds
- `bin\Release\net48\.env` for Release builds

## Architecture

```
User Prompt
    ↓
GPT-4 API (parameter extraction)
    ↓
AirplaneParameters
    ↓
AirplaneGenerator (SolidWorks API)
    ↓
Parametric SolidWorks Part
```

### Components Generated

1. **Fuselage**: Extruded cylinder with tapered nose cone
2. **Wings**: Swept/delta/straight planform, proper airfoil
3. **Tail**: Horizontal + vertical stabilizers
4. **Engines**: Wing-mounted nacelles (2 or 4)
5. **Canopy**: Revolved dome for cockpit

All features are fully parametric and can be edited in the feature tree!

## Project Structure

```
AirplaneSolidWorksAddin/
├── src/
│   ├── AirplaneAddin.cs         # Main add-in (ISwAddin)
│   ├── AirplaneGenerator.cs     # SolidWorks geometry generation
│   ├── LLMService.cs             # OpenAI GPT integration
│   ├── TaskpaneControl.cs       # UI panel
│   └── EnvLoader.cs             # .env file loader
├── .env.example                  # Template for .env file
├── .env                          # Your API keys (gitignored)
├── Register.bat                  # COM registration script
├── Unregister.bat               # COM removal script
├── AirplaneSolidWorksAddin.csproj
├── AirplaneSolidWorksAddin.sln
└── README.md
```

## Troubleshooting

### "OPENAI_API_KEY not configured"

**Fix:**
1. Make sure `.env` file exists in project root
2. Add your API key: `OPENAI_API_KEY=sk-proj-your-key`
3. Copy `.env` to `bin\Debug\net48\` or `bin\Release\net48\`
4. Restart SolidWorks

### Add-in doesn't appear in Tools > Add-Ins

**Fix:**
1. Close SolidWorks
2. Run `Register.bat` as Administrator again
3. Check for success message
4. Open SolidWorks
5. Check Tools > Add-Ins

### "Could not load file SolidWorks.Interop.sldworks"

**Fix:**
1. Update `<SolidWorksPath>` in `.csproj`
2. Make sure you have SolidWorks SDK installed
3. Clean and rebuild solution

### Generation fails with no error

**Fix:**
1. Check if a new part document was created
2. Look at SolidWorks status bar for messages
3. Try simpler prompt: "small fighter jet"
4. Check Windows Event Viewer > Application logs
5. Verify API key is valid and has credits

### API Rate Limits

If you hit OpenAI rate limits:
1. Use `gpt-3.5-turbo` for faster, cheaper calls
2. Add delays between generations
3. Upgrade your OpenAI plan

## Customization

### Modify AI Behavior

Edit `src/LLMService.cs:ParseAirplanePrompt()` system prompt to change how parameters are extracted.

### Add New Components

Edit `src/AirplaneGenerator.cs` to add:
- Landing gear
- Windows
- More detailed engines
- Control surfaces (flaps, ailerons)
- Weapon hardpoints

### Change Default Values

Edit `src/LLMService.cs:GetDefaultParameters()`.

### Custom UI

Edit `src/TaskpaneControl.cs` to customize the interface.

## Development

### Debug in Visual Studio

1. Set SolidWorks as external program:
   - Project Properties > Debug
   - Start external program: `C:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\SLDWORKS.exe`
2. Press F5 to debug
3. SolidWorks launches with add-in attached

### Rebuild After Changes

```cmd
Clean Solution
Rebuild Solution
Copy .env to bin\Debug\net48\
Run Register.bat as admin (if COM interface changed)
Restart SolidWorks
```

## Performance

- **AI Processing**: 2-5 seconds (OpenAI API call)
- **Geometry Generation**: 3-10 seconds (depending on complexity)
- **Total Time**: 5-15 seconds from prompt to model

## Cost Estimation

Using GPT-4:
- ~$0.01-0.03 per airplane generation
- 100 airplanes ≈ $1-3

Using GPT-3.5-turbo:
- ~$0.001-0.003 per generation
- 1000 airplanes ≈ $1-3

## Limitations

- Basic airplane shapes (not production-ready designs)
- Simplified aerodynamics (not flight-tested)
- No internal structure or systems
- Requires internet connection for AI

## Future Enhancements

- [ ] Save/load custom airplane configurations
- [ ] More detailed engine nacelles
- [ ] Landing gear (retractable)
- [ ] Windows along fuselage
- [ ] Winglets and control surfaces
- [ ] Multi-material assignment
- [ ] Batch generation from CSV
- [ ] Integration with SolidWorks Simulation
- [ ] Offline mode with cached parameters

## License

MIT License - Free for hackathon use and modification!

## Credits

Built for Hack Nation hackathon using:
- SolidWorks API
- OpenAI GPT-4
- .NET Framework 4.8

## Support

For issues or questions:
1. Check SETUP_GUIDE.md for detailed instructions
2. Review troubleshooting section above
3. Check SolidWorks API documentation
4. Verify OpenAI API key and credits

---

**Happy modeling!** Generate hundreds of airplane variations in minutes instead of hours of manual CAD work.
