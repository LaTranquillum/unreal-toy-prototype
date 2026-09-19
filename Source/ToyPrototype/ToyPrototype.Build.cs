using UnrealBuildTool;
public class ToyPrototype : ModuleRules { public ToyPrototype(ReadOnlyTargetRules Target) : base(Target) { PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs; PublicDependencyModuleNames.AddRange(new string[] {"Core", "CoreUObject", "Engine", "InputCore", "AIModule", "NavigationSystem", "AnimGraphRuntime", "PhysicsCore", "Json", "JsonUtilities"}); } }
