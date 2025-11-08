# Setup Guide - Complete Step-by-Step Instructions

## Part 1: Prerequisites (10 minutes)

### 1. Check SolidWorks Installation

1. Open SolidWorks
2. Help > About SolidWorks
3. Note your version (e.g., "SolidWorks 2024 SP3.0")
4. Note installation path (usually `C:\Program Files\SOLIDWORKS Corp\SOLIDWORKS`)

### 2. Install Visual Studio 2022

If you don't have it:

1. Download [Visual Studio 2022 Community](https://visualstudio.microsoft.com/downloads/) (free)
2. Run installer
3. Select workloads:
   - ✅ **.NET desktop development**
4. Click Install (takes 15-20 minutes)
5. Restart computer

### 3. Verify .NET Framework 4.8

Usually included with Visual Studio, but verify:

1. Open Command Prompt
2. Run:
   ```cmd
   reg query "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\NET Framework Setup\NDP\v4\Full" /v Version
   ```
3. Should show version 4.8.x

If not installed:
- Download from [Microsoft](https://dotnet.microsoft.com/download/dotnet-framework/net48)

### 4. Get Anthropic API Key

1. Go to [console.anthropic.com](https://console.anthropic.com)
2. Sign up or log in
3. Navigate to **API Keys** in left sidebar
4. Click **Create Key**
5. Name it "SolidWorks Plugin"
6. **Copy the key** (starts with `sk-ant-`)
7. Keep it safe!

### 5. Set Environment Variable

**IMPORTANT: Must run as Administrator**

1. Press `Win + X`
2. Select "Command Prompt (Admin)" or "PowerShell (Admin)"
3. Run:
   ```cmd
   setx ANTHROPIC_API_KEY "sk-ant-your-actual-key-here"
   ```
4. You should see: "SUCCESS: Specified value was saved."
5. Close the admin terminal

## Part 2: Build the Add-in (15 minutes)

### 1. Open Solution

1. Navigate to:
   ```
   Desktop\hackathons\hacknation-nat\AirplaneSolidWorksAddin\
   ```
2. Double-click `AirplaneSolidWorksAddin.sln`
3. Visual Studio opens

### 2. Configure SolidWorks Path

1. In Solution Explorer, double-click `AirplaneSolidWorksAddin.csproj`
2. Find this line:
   ```xml
   <SolidWorksPath>C:\Program Files\SOLIDWORKS Corp\SOLIDWORKS</SolidWorksPath>
   ```
3. Update if your SolidWorks is installed elsewhere
4. Save file (Ctrl+S)

### 3. Restore NuGet Packages

1. Tools > NuGet Package Manager > Package Manager Console
2. Run:
   ```
   Update-Package -reinstall
   ```
3. Wait for packages to download (Anthropic SDK, etc.)

### 4. Build the Project

1. Set configuration to **Debug** (dropdown at top)
2. Build > Build Solution (or press F6)
3. Wait for build to complete
4. Check Output window for:
   ```
   ========== Build: 1 succeeded, 0 failed ==========
   ```

If you see errors:
- **Missing references**: Check SolidWorks path in step 2
- **NuGet errors**: Try step 3 again
- **Syntax errors**: You may have a corrupted file

### 5. Locate Built DLL

Your add-in DLL is at:
```
Desktop\hackathons\hacknation-nat\AirplaneSolidWorksAddin\bin\Debug\net48\AirplaneSolidWorksAddin.dll
```

## Part 3: Register with SolidWorks (5 minutes)

### 1. Run Registration Script

**CRITICAL: Must run as Administrator**

1. Navigate to:
   ```
   Desktop\hackathons\hacknation-nat\AirplaneSolidWorksAddin\
   ```
2. Right-click `Register.bat`
3. Select **"Run as administrator"**
4. A command window opens

Expected output:
```
========================================
  SolidWorks Add-in Registration
========================================

Found DLL at: [...]\AirplaneSolidWorksAddin.dll

Registering add-in...
Microsoft .NET Framework Assembly Registration Utility version [...]
Copyright (C) Microsoft Corporation. All rights reserved.

Types registered successfully

========================================
  Registration Successful!
========================================

The add-in is now registered with SolidWorks.
Restart SolidWorks and go to Tools > Add-Ins
to enable "Airplane Generator"

Press any key to continue...
```

If you see errors:
- **"not recognized as an administrator"**: Right-click and select "Run as administrator"
- **"Could not find DLL"**: Build the project first (Part 2)
- **"Access denied"**: Disable antivirus temporarily

## Part 4: Enable in SolidWorks (5 minutes)

### 1. Open SolidWorks

If already open, close and restart.

### 2. Enable Add-in

1. Go to **Tools > Add-Ins...**
2. Find **"Airplane Generator"** in the list
3. Check BOTH columns:
   - ✅ Active Add-ins (runs now)
   - ✅ Start Up (loads automatically)
4. Click **OK**

### 3. Verify Installation

You should see:
- **Toolbar**: "Airplane Generator" buttons appear
- **Menu**: Tools > Airplane Generator submenu
- **Task Pane**: Right side panel with "Airplane Generator"

If you don't see it:
- Check Tools > Add-Ins again
- Look for error messages in SolidWorks status bar
- Check Windows Event Viewer > Application logs

## Part 5: First Test (10 minutes)

### 1. Open Task Pane

1. Look for "Airplane Generator" panel on right side
2. If not visible: Tools > Airplane Generator > Show Panel

### 2. Generate Your First Airplane

1. In the task pane text box, enter:
   ```
   Fighter jet with swept wings, 15 meter wingspan, twin engines
   ```
2. Click **"Generate Airplane"** button
3. Wait for progress dialog:
   - "Analyzing prompt with AI..." (3-5 sec)
   - "Generating 3D model..." (5-10 sec)
4. Success dialog appears
5. Your airplane model appears in SolidWorks!

### 3. Explore the Model

1. **Rotate view**: Middle mouse drag
2. **Feature tree**: Left side shows all features
   - Boss-Extrude1 (fuselage)
   - Boss-Extrude2, 3 (wings)
   - Boss-Extrude4, 5, 6 (tail)
   - Boss-Extrude7, 8 (engines)
3. **Edit features**: Right-click any feature > Edit Feature
4. **Measure**: Tools > Evaluate > Measure

### 4. Try Different Prompts

Double-click examples in task pane:
- "Commercial airliner, 60m wingspan"
- "Small propeller plane, high wings"
- "Stealth bomber, flying wing design"

Each generates a new part document.

### 5. Export to STL

1. File > Save As
2. Save as type: **STL (*.stl)**
3. Click **Options**:
   - Quality: Fine
   - Units: Millimeters
   - Format: Binary
4. Click OK
5. Enter filename: `my_fighter_jet.stl`
6. Save

You now have an STL ready for 3D printing or CAD analysis!

## Troubleshooting

### Issue: "ANTHROPIC_API_KEY not set"

**Symptoms**: Error dialog when clicking Generate

**Fix:**
1. Open NEW Command Prompt as Administrator
2. Run:
   ```cmd
   setx ANTHROPIC_API_KEY "sk-ant-your-key-here"
   ```
3. Verify:
   ```cmd
   echo %ANTHROPIC_API_KEY%
   ```
   Should print your key
4. Close SolidWorks completely
5. Reopen SolidWorks

### Issue: Add-in not in Tools > Add-Ins list

**Symptoms**: Can't find "Airplane Generator"

**Fix:**
1. Close SolidWorks
2. Run `Register.bat` as Administrator again
3. Check for success message
4. Open SolidWorks
5. Check Tools > Add-Ins

If still not there:
1. Open Registry Editor (Win + R, type `regedit`)
2. Navigate to:
   ```
   HKEY_LOCAL_MACHINE\SOFTWARE\SolidWorks\Addins\{8B5E9A2C-4F3D-4E1A-9B2C-7D8E6F5A4B3C}
   ```
3. If missing, registration failed - check Windows Event Viewer

### Issue: Generation starts but fails silently

**Symptoms**: Progress dialog shows but no model appears

**Fix:**
1. Check SolidWorks status bar for error messages
2. Try simpler prompt: "small airplane"
3. Check if new part document was created (might be empty)
4. Look at Windows Event Viewer > Application logs for exceptions

### Issue: Model looks incorrect or distorted

**Symptoms**: Airplane generates but looks wrong

**Fix:**
1. Try more specific prompt with exact dimensions:
   ```
   Fighter jet, 12 meter wingspan, 10 meter fuselage, swept wings
   ```
2. Check extracted parameters in progress dialog
3. Edit features manually in feature tree to correct

### Issue: Visual Studio build errors

**Error: "Could not load SolidWorks.Interop.sldworks"**

**Fix:**
1. Update `<SolidWorksPath>` in `.csproj`
2. Ensure SolidWorks API redist DLLs exist:
   ```
   [SolidWorks]\api\redist\SolidWorks.Interop.sldworks.dll
   ```
3. Clean solution: Build > Clean Solution
4. Rebuild: Build > Rebuild Solution

**Error: "The type or namespace name 'Anthropic' could not be found"**

**Fix:**
1. Tools > NuGet Package Manager > Package Manager Console
2. Run:
   ```
   Install-Package Anthropic.SDK
   ```
3. Rebuild

### Issue: Registration fails

**Error: "Registration failed" or "Access denied"**

**Fix:**
1. Close all instances of SolidWorks
2. Run Command Prompt as Administrator:
   ```cmd
   cd "C:\Windows\Microsoft.NET\Framework64\v4.0.30319"
   RegAsm.exe /codebase "PATH\TO\AirplaneSolidWorksAddin.dll"
   ```
3. Look for specific error messages
4. Temporarily disable antivirus
5. Check if DLL is blocked: Right-click DLL > Properties > Unblock

## Advanced Usage

### Debug in Visual Studio

1. Project Properties > Debug
2. Start external program:
   ```
   C:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\SLDWORKS.exe
   ```
3. Press F5
4. SolidWorks launches with debugger attached
5. Set breakpoints in code
6. Step through generation process

### Modify AI Prompts

1. Open `src\LLMService.cs`
2. Edit `ParseAirplanePrompt()` method
3. Modify the `systemPrompt` string
4. Rebuild and re-register

### Customize UI

1. Open `src\TaskpaneControl.cs`
2. Modify `InitializeComponent()` method
3. Add new buttons, textboxes, etc.
4. Rebuild

## Hackathon Demo Tips

### Quick Demo Flow (5 minutes)

1. **Intro** (30 sec):
   - "AI-powered airplane generator for SolidWorks"
   - "Plain English to CAD in seconds"

2. **Live Demo** (2 min):
   - Type: "Fighter jet with delta wings, 20m wingspan"
   - Show AI processing
   - Show generated model rotating

3. **Show Features** (1 min):
   - Open feature tree
   - Edit a dimension
   - Show it updates parametrically

4. **Export** (30 sec):
   - File > Save As > STL
   - "Ready for 3D printing or simulation"

5. **Variations** (1 min):
   - Generate 2-3 different types quickly
   - Show: fighter, commercial, propeller
   - "Manual CAD would take hours each"

### Backup Plans

1. **API fails**: Have pre-generated models open
2. **Slow internet**: Demo with cached responses (add offline mode)
3. **SolidWorks crashes**: Have screenshots/video

### Impressive Prompts

```
"F-22 Raptor style stealth fighter, 13.56 meter wingspan, twin engines"
"Boeing 747 style jumbo jet, 64 meter wingspan, 4 engines"
"Cessna style propeller plane, high wing, 11 meter wingspan"
```

## Next Steps

1. **Enhance geometry**: Add landing gear, windows, control surfaces
2. **Material assignment**: Auto-assign aluminum/composite materials
3. **Configuration tables**: Generate size variations
4. **Batch mode**: CSV input for multiple airplanes
5. **Simulation ready**: Auto-setup for CFD or FEA

## Resources

- [SolidWorks API Documentation](https://help.solidworks.com/api)
- [Anthropic API Docs](https://docs.anthropic.com)
- [.NET Framework Reference](https://learn.microsoft.com/dotnet)

Good luck with your hackathon! 🚀✈️
