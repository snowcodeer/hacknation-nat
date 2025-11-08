using System;
using SolidWorks.Interop.sldworks;
using SolidWorks.Interop.swconst;

namespace AirplaneSolidWorksAddin
{
    public class AirplaneGenerator
    {
        private readonly ISldWorks _swApp;
        private readonly AirplaneParameters _params;
        private ModelDoc2? _model;
        private const double MetersToMillimeters = 1000.0; // SolidWorks uses mm

        public AirplaneGenerator(ISldWorks swApp, AirplaneParameters parameters)
        {
            _swApp = swApp;
            _params = parameters;
        }

        public bool Generate()
        {
            try
            {
                // Create new part document
                _model = (ModelDoc2)_swApp.NewDocument(
                    _swApp.GetUserPreferenceStringValue((int)swUserPreferenceStringValue_e.swDefaultTemplatePart),
                    (int)swDwgPaperSizes_e.swDwgPaperA,
                    0, 0);

                if (_model == null)
                    return false;

                // Generate components
                CreateFuselage();
                CreateWings();
                CreateTail();
                CreateEngines();

                if (_params.HasCanopy)
                {
                    CreateCanopy();
                }

                // Rebuild and zoom to fit
                _model.ForceRebuild3(true);
                _model.ViewZoomtofit2();

                return true;
            }
            catch (Exception ex)
            {
                System.Windows.Forms.MessageBox.Show(
                    $"Generation error: {ex.Message}\n\n{ex.StackTrace}",
                    "Error");
                return false;
            }
        }

        private void CreateFuselage()
        {
            // Select Front plane
            _model!.Extension.SelectByID2("Front Plane", "PLANE", 0, 0, 0, false, 0, null, 0);

            // Create sketch
            _model.SketchManager.InsertSketch(true);

            double fuselageLength = _params.FuselageLength * MetersToMillimeters;
            double fuselageRadius = _params.FuselageRadius * MetersToMillimeters;
            double noseLength = _params.NoseLength * MetersToMillimeters;

            // Draw fuselage profile as circle
            _model.SketchManager.CreateCircleByRadius(0, 0, 0, fuselageRadius);

            // Exit sketch
            _model.SketchManager.InsertSketch(true);

            // Extrude the fuselage body
            _model.Extension.SelectByID2("Sketch1", "SKETCH", 0, 0, 0, false, 0, null, 0);

            FeatureManager featMgr = _model.FeatureManager;
            featMgr.FeatureExtrusion3(
                true, false, false,
                (int)swEndConditions_e.swEndCondBlind, 0,
                fuselageLength / 1000.0, 0, // Convert back to meters for extrusion
                false, false, false, false,
                0, 0, false, false, false, false, true, true, true,
                (int)swStartConditions_e.swStartSketchPlane, 0, false);

            // Add nose cone
            CreateNoseCone(fuselageLength, fuselageRadius, noseLength);
        }

        private void CreateNoseCone(double fuselageLength, double fuselageRadius, double noseLength)
        {
            try
            {
                // Select plane at end of fuselage for nose
                _model!.Extension.SelectByID2("Front Plane", "PLANE", 0, 0, 0, false, 0, null, 0);

                // Create offset plane
                _model.FeatureManager.InsertRefPlane(
                    (int)swRefPlaneReferenceConstraints_e.swRefPlaneReferenceConstraint_Distance,
                    fuselageLength / 1000.0, 0, 0, 0, 0);

                // Select the new plane
                Feature plane = (Feature)_model.FeatureByPositionReverse(0);
                plane.Select2(false, 0);

                // Create sketch on new plane
                _model.SketchManager.InsertSketch(true);

                // Draw small circle for nose tip
                _model.SketchManager.CreateCircleByRadius(0, 0, 0, fuselageRadius * 0.2);

                _model.SketchManager.InsertSketch(true);

                // Loft between fuselage end and nose tip
                // This creates the tapered nose
                _model.InsertCutBlend2(true, true);
            }
            catch
            {
                // If nose creation fails, continue without it
            }
        }

        private void CreateWings()
        {
            double wingspan = _params.Wingspan * MetersToMillimeters / 2; // Half span
            double wingChord = _params.FuselageLength * MetersToMillimeters * 0.25;
            double wingPosition = _params.FuselageLength * MetersToMillimeters * 0.4;
            double sweepAngle = _params.WingSweepAngle * Math.PI / 180.0;

            // Right wing
            CreateWing(wingspan, wingChord, wingPosition, sweepAngle, false);

            // Left wing (mirror)
            CreateWing(wingspan, wingChord, wingPosition, sweepAngle, true);
        }

        private void CreateWing(double span, double chord, double position, double sweepAngle, bool isLeft)
        {
            try
            {
                // Select Top plane
                _model!.Extension.SelectByID2("Top Plane", "PLANE", 0, 0, 0, false, 0, null, 0);

                // Create sketch
                _model.SketchManager.InsertSketch(true);

                double direction = isLeft ? -1 : 1;
                double sweepOffset = span * Math.Tan(sweepAngle);

                // Convert to meters for sketch
                double posM = position / 1000.0;
                double spanM = (span / 1000.0) * direction;
                double chordM = chord / 1000.0;
                double sweepM = sweepOffset / 1000.0;

                // Draw wing profile (quadrilateral)
                object[] points = new object[5];
                points[0] = _model.SketchManager.CreatePoint(posM, 0, 0);
                points[1] = _model.SketchManager.CreatePoint(posM - chordM, 0, 0);
                points[2] = _model.SketchManager.CreatePoint(posM - chordM * 0.7 - sweepM, spanM, 0);
                points[3] = _model.SketchManager.CreatePoint(posM - sweepM, spanM, 0);

                // Connect with lines
                _model.SketchManager.CreateLine(posM, 0, 0, posM - chordM, 0, 0);
                _model.SketchManager.CreateLine(posM - chordM, 0, 0, posM - chordM * 0.7 - sweepM, spanM, 0);
                _model.SketchManager.CreateLine(posM - chordM * 0.7 - sweepM, spanM, 0, posM - sweepM, spanM, 0);
                _model.SketchManager.CreateLine(posM - sweepM, spanM, 0, posM, 0, 0);

                _model.SketchManager.InsertSketch(true);

                // Extrude wing with thickness
                _model.Extension.SelectByID2($"Sketch{GetNextSketchNumber()}", "SKETCH", 0, 0, 0, false, 0, null, 0);

                double wingThickness = _params.FuselageRadius * MetersToMillimeters * 0.15;
                _model.FeatureManager.FeatureExtrusion3(
                    true, false, false,
                    (int)swEndConditions_e.swEndCondMidPlane, 0,
                    wingThickness / 1000.0, 0,
                    false, false, false, false,
                    0, 0, false, false, false, false, true, true, true,
                    (int)swStartConditions_e.swStartSketchPlane, 0, false);
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Wing creation error: {ex.Message}");
            }
        }

        private void CreateTail()
        {
            double tailPosition = -_params.FuselageLength * MetersToMillimeters * 0.1;
            double tailSpan = _params.Wingspan * MetersToMillimeters * 0.25;
            double tailChord = _params.FuselageLength * MetersToMillimeters * 0.15;

            // Horizontal stabilizer (right)
            CreateTailSurface(tailPosition, tailSpan / 2, tailChord, false, false);

            // Horizontal stabilizer (left)
            CreateTailSurface(tailPosition, tailSpan / 2, tailChord, true, false);

            // Vertical stabilizer
            CreateVerticalTail(tailPosition, _params.TailHeight * MetersToMillimeters, tailChord);
        }

        private void CreateTailSurface(double position, double span, double chord, bool isLeft, bool isVertical)
        {
            try
            {
                string plane = isVertical ? "Front Plane" : "Top Plane";
                _model!.Extension.SelectByID2(plane, "PLANE", 0, 0, 0, false, 0, null, 0);

                _model.SketchManager.InsertSketch(true);

                double direction = isLeft ? -1 : 1;
                double posM = position / 1000.0;
                double spanM = (span / 1000.0) * direction;
                double chordM = chord / 1000.0;

                // Simple rectangular tail
                _model.SketchManager.CreateLine(posM, 0, 0, posM - chordM, 0, 0);
                _model.SketchManager.CreateLine(posM - chordM, 0, 0, posM - chordM, spanM, 0);
                _model.SketchManager.CreateLine(posM - chordM, spanM, 0, posM, spanM, 0);
                _model.SketchManager.CreateLine(posM, spanM, 0, posM, 0, 0);

                _model.SketchManager.InsertSketch(true);

                _model.Extension.SelectByID2($"Sketch{GetNextSketchNumber()}", "SKETCH", 0, 0, 0, false, 0, null, 0);

                double thickness = _params.FuselageRadius * MetersToMillimeters * 0.1;
                _model.FeatureManager.FeatureExtrusion3(
                    true, false, false,
                    (int)swEndConditions_e.swEndCondMidPlane, 0,
                    thickness / 1000.0, 0,
                    false, false, false, false,
                    0, 0, false, false, false, false, true, true, true,
                    (int)swStartConditions_e.swStartSketchPlane, 0, false);
            }
            catch { }
        }

        private void CreateVerticalTail(double position, double height, double chord)
        {
            try
            {
                _model!.Extension.SelectByID2("Right Plane", "PLANE", 0, 0, 0, false, 0, null, 0);

                _model.SketchManager.InsertSketch(true);

                double posM = position / 1000.0;
                double heightM = height / 1000.0;
                double chordM = chord / 1000.0;

                // Draw vertical stabilizer profile
                _model.SketchManager.CreateLine(posM, 0, 0, posM - chordM, 0, 0);
                _model.SketchManager.CreateLine(posM - chordM, 0, 0, posM - chordM * 0.7, heightM, 0);
                _model.SketchManager.CreateLine(posM - chordM * 0.7, heightM, 0, posM, 0, 0);

                _model.SketchManager.InsertSketch(true);

                _model.Extension.SelectByID2($"Sketch{GetNextSketchNumber()}", "SKETCH", 0, 0, 0, false, 0, null, 0);

                double thickness = _params.FuselageRadius * MetersToMillimeters * 0.1;
                _model.FeatureManager.FeatureExtrusion3(
                    true, false, false,
                    (int)swEndConditions_e.swEndCondMidPlane, 0,
                    thickness / 1000.0, 0,
                    false, false, false, false,
                    0, 0, false, false, false, false, true, true, true,
                    (int)swStartConditions_e.swStartSketchPlane, 0, false);
            }
            catch { }
        }

        private void CreateEngines()
        {
            if (_params.EngineCount == 0)
                return;

            double engineRadius = _params.FuselageRadius * MetersToMillimeters * 0.35;
            double engineLength = _params.FuselageLength * MetersToMillimeters * 0.2;
            double enginePosition = _params.FuselageLength * MetersToMillimeters * 0.35;

            if (_params.EngineCount == 2)
            {
                double engineY = _params.Wingspan * MetersToMillimeters * 0.2;
                CreateEngine(enginePosition, engineY, -engineRadius * 1.5, engineRadius, engineLength);
                CreateEngine(enginePosition, -engineY, -engineRadius * 1.5, engineRadius, engineLength);
            }
            else if (_params.EngineCount == 4)
            {
                double innerY = _params.Wingspan * MetersToMillimeters * 0.15;
                double outerY = _params.Wingspan * MetersToMillimeters * 0.35;
                CreateEngine(enginePosition, innerY, -engineRadius * 1.5, engineRadius, engineLength);
                CreateEngine(enginePosition, -innerY, -engineRadius * 1.5, engineRadius, engineLength);
                CreateEngine(enginePosition - 500, outerY, -engineRadius * 1.5, engineRadius, engineLength);
                CreateEngine(enginePosition - 500, -outerY, -engineRadius * 1.5, engineRadius, engineLength);
            }
        }

        private void CreateEngine(double x, double y, double z, double radius, double length)
        {
            try
            {
                // Create offset plane for engine
                _model!.Extension.SelectByID2("Right Plane", "PLANE", 0, 0, 0, false, 0, null, 0);

                _model.SketchManager.InsertSketch(true);

                // Draw circle for engine
                _model.SketchManager.CreateCircleByRadius(
                    x / 1000.0,
                    y / 1000.0,
                    0,
                    radius / 1000.0);

                _model.SketchManager.InsertSketch(true);

                _model.Extension.SelectByID2($"Sketch{GetNextSketchNumber()}", "SKETCH", 0, 0, 0, false, 0, null, 0);

                _model.FeatureManager.FeatureExtrusion3(
                    true, false, false,
                    (int)swEndConditions_e.swEndCondMidPlane, 0,
                    length / 1000.0, 0,
                    false, false, false, false,
                    0, 0, false, false, false, false, true, true, true,
                    (int)swStartConditions_e.swStartSketchPlane, 0, false);
            }
            catch { }
        }

        private void CreateCanopy()
        {
            try
            {
                double canopyPosition = _params.FuselageLength * MetersToMillimeters * 0.65;
                double canopyRadius = _params.FuselageRadius * MetersToMillimeters * 0.7;

                // Create canopy as sphere
                _model!.Extension.SelectByID2("Front Plane", "PLANE", 0, 0, 0, false, 0, null, 0);

                // Create offset plane
                _model.FeatureManager.InsertRefPlane(
                    (int)swRefPlaneReferenceConstraints_e.swRefPlaneReferenceConstraint_Distance,
                    canopyPosition / 1000.0, 0, 0, 0, 0);

                Feature plane = (Feature)_model.FeatureByPositionReverse(0);
                plane.Select2(false, 0);

                _model.SketchManager.InsertSketch(true);

                // Draw semicircle for canopy
                _model.SketchManager.CreateArc(
                    0, 0, 0,
                    0, canopyRadius / 1000.0, 0,
                    0, -canopyRadius / 1000.0, 0,
                    1);

                // Close with line
                _model.SketchManager.CreateLine(
                    0, canopyRadius / 1000.0, 0,
                    0, -canopyRadius / 1000.0, 0);

                _model.SketchManager.InsertSketch(true);

                // Revolve to create dome
                _model.Extension.SelectByID2($"Sketch{GetNextSketchNumber()}", "SKETCH", 0, 0, 0, false, 0, null, 0);
                _model.Extension.SelectByID2("Line1", "SKETCHSEGMENT", 0, 0, 0, true, 2, null, 0);

                _model.FeatureManager.FeatureRevolve2(
                    true, true, false, false, false, false,
                    0, 0, 360.0 * Math.PI / 180.0, 0,
                    false, false, 0, 0, 0, 0, 0, true, true, true);
            }
            catch { }
        }

        private int _sketchCounter = 1;
        private int GetNextSketchNumber()
        {
            return _sketchCounter++;
        }
    }
}
