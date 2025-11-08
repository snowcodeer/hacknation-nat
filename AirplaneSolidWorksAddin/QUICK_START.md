# Quick Start - 5 Minute Guide

## Setup (Once)

1. **Configure API Key**:
   - Copy `.env.example` to `.env`
   - Edit `.env`:
     ```
     OPENAI_API_KEY=sk-proj-your-key-here
     ```

2. **Build** (Visual Studio):
   - Open `AirplaneSolidWorksAddin.sln`
   - Press F6 to build

3. **Copy .env file**:
   - Copy `.env` to `bin\Debug\net48\`

4. **Register** (Run as Admin):
   - Right-click `Register.bat`
   - Run as administrator

5. **Enable** (SolidWorks):
   - Tools > Add-Ins
   - Check "Airplane Generator" (both columns)

## Usage

### Generate Airplane

1. Open "Airplane Generator" task pane (right side)
2. Enter description:
   ```
   Fighter jet with swept wings, 15m wingspan
   ```
3. Click "Generate Airplane"
4. Wait 10 seconds
5. Done!

### Export to STL

1. File > Save As
2. Save as type: **STL (*.stl)**
3. Save

## Example Prompts

```
Fighter jet with swept wings, 15 meter wingspan, twin engines
Commercial airliner, wide body, 60m wingspan, 4 engines
Small propeller plane with high wings
Stealth bomber with flying wing design
Business jet, sleek design, 12m wingspan
```

## Configuration

Edit `.env` file:
```bash
OPENAI_API_KEY=sk-proj-your-key
OPENAI_MODEL=gpt-4          # or gpt-4-turbo, gpt-3.5-turbo
OPENAI_TEMPERATURE=0.3      # 0.0-1.0, lower = more consistent
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| API key error | Make sure .env is in bin\Debug\net48\ |
| Add-in not showing | Run Register.bat as admin |
| Build errors | Update SolidWorks path in .csproj |
| Generation fails | Try simpler prompt: "small fighter jet" |
| Rate limits | Use gpt-3.5-turbo for cheaper calls |

## Files

- `.env.example` - Template (copy to .env)
- `.env` - Your API key (gitignored)
- `AirplaneSolidWorksAddin.sln` - Open in Visual Studio
- `Register.bat` - Run as admin after building
- `README.md` - Full documentation
- `SETUP_GUIDE.md` - Detailed step-by-step

## Cost

- **GPT-4**: ~$0.01-0.03 per airplane
- **GPT-3.5-turbo**: ~$0.001-0.003 per airplane

## Support

See SETUP_GUIDE.md for detailed troubleshooting.
