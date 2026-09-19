using UnrealBuildTool;
public class ToyPrototypeTarget : TargetRules { public ToyPrototypeTarget(TargetInfo Target) : base(Target) { Type = TargetType.Game; DefaultBuildSettings = BuildSettingsVersion.V7; IncludeOrderVersion = EngineIncludeOrderVersion.Unreal5_8; ExtraModuleNames.Add("ToyPrototype"); } }
