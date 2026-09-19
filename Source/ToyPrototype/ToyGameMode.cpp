#include "ToyGameMode.h"
#include "ToyPlayerController.h"
#include "InputKeyEventArgs.h"
#include "Engine/World.h"
#include "NavigationSystem.h"
#include "TimerManager.h"
#include "Engine/GameViewportClient.h"
#if WITH_EDITOR
#include "ShaderCompiler.h"
#endif
#include "ToyCharacter.h"
#include "ToyAIController.h"
#include "ToyAnimInstance.h"
#include "EngineUtils.h"
#include "Engine/Canvas.h"
#include "Engine/StaticMeshActor.h"
#include "Engine/StaticMesh.h"
#include "Components/StaticMeshComponent.h"
#include "Components/CapsuleComponent.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Camera/CameraActor.h"
#include "Camera/CameraComponent.h"
#include "Kismet/GameplayStatics.h"
#include "Serialization/JsonSerializer.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "HAL/PlatformFileManager.h"
#include "HAL/PlatformMisc.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"

AToyGameMode::AToyGameMode()
{
    DefaultPawnClass=nullptr;
    HUDClass=AToyHUD::StaticClass();
    PlayerControllerClass=AToyPlayerController::StaticClass();
    PrimaryActorTick.bCanEverTick=true;
}
void AToyGameMode::BeginPlay()
{
    Super::BeginPlay();
    if(TActorIterator<AToyCharacter> It{GetWorld()}; It) { Toy=*It; }
    if(!Toy) Toy=GetWorld()->SpawnActor<AToyCharacter>(FVector(-450,-300,90),FRotator::ZeroRotator);
    ACameraActor* Camera=nullptr;
    if(TActorIterator<ACameraActor> It{GetWorld()}; It) { Camera=*It; }
    if(Camera) if(APlayerController* PC=GetWorld()->GetFirstPlayerController()) { PC->SetViewTarget(Camera); PC->bShowMouseCursor=true; }
    // Editor commandlets can save a registered Recast actor with no usable tiles.
    // Rebuild after all level collision and navigation bounds have registered.
    GetWorldTimerManager().SetTimerForNextTick([this]()
    {
        if(UNavigationSystemV1* Nav=FNavigationSystem::GetCurrent<UNavigationSystemV1>(GetWorld()))
        {
            Nav->Build();
            UE_LOG(LogTemp,Display,TEXT("TOY requested initial navigation build"));
        }
    });
    bCapture=FParse::Param(FCommandLine::Get(),TEXT("ToyCapture"));
    bVerify=FParse::Param(FCommandLine::Get(),TEXT("ToyVerify"));
    if(bCapture && Toy) { Toy->IdleWeight=1; Toy->WanderWeight=Toy->LookWeight=Toy->GestureWeight=0; }
    if(bVerify && Toy)
    {
        Toy->WanderWeight=1; Toy->IdleWeight=Toy->LookWeight=Toy->GestureWeight=0;
        Toy->PauseMin=.4f; Toy->PauseMax=.7f;
    }
}
void AToyGameMode::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);
    if(!Toy) return;
    AToyAIController* AI=Cast<AToyAIController>(Toy->GetController());
    if(!AI) return;
    if(APlayerController* PC=GetWorld()->GetFirstPlayerController())
    {
        if(ACameraActor* Camera=Cast<ACameraActor>(PC->GetViewTarget()))
        {
            const FVector Goal=Toy->GetActorLocation()+FVector(650,-900,650);
            Camera->SetActorLocation(FMath::VInterpTo(Camera->GetActorLocation(),Goal,DeltaSeconds,3.f));
            Camera->SetActorRotation((Toy->GetActorLocation()+FVector(0,0,15)-Camera->GetActorLocation()).Rotation());
        }
    }
#if WITH_EDITOR
    // Do not capture grey fallback materials while first-time shaders compile.
    if(bCapture && GShaderCompilingManager && GShaderCompilingManager->IsCompiling()) return;
#endif
    Age+=DeltaSeconds;
    if(bCapture)
    {
        if(Age>3 && CapturePhase==0) { AI->ForceIntent(EToyIntent::LookAround); CapturePhase=1; }
        if(Age>4 && CapturePhase==1) { FScreenshotRequest::RequestScreenshot(FPaths::ProjectSavedDir()/TEXT("Verification/01-look.png"),true,false); CapturePhase=2; }
        if(Age>7 && CapturePhase==2) { AI->ForceIntent(EToyIntent::Gesture); Toy->PerturbOnce(); CapturePhase=3; }
        if(Age>8 && CapturePhase==3) { FScreenshotRequest::RequestScreenshot(FPaths::ProjectSavedDir()/TEXT("Verification/02-gesture.png"),true,false); CapturePhase=4; }
        if(Age>11 && CapturePhase==4) { AI->ForceIntent(EToyIntent::Wander); CapturePhase=5; }
        if(Age>13 && CapturePhase==5) { FScreenshotRequest::RequestScreenshot(FPaths::ProjectSavedDir()/TEXT("Verification/03-walk.png"),true,false); CapturePhase=6; }
        if(Age>16 && CapturePhase==6) { AI->SetManualIntent(EToyIntent::Hop); CapturePhase=7; }
        if(Age>16.3 && CapturePhase==7) { FScreenshotRequest::RequestScreenshot(FPaths::ProjectSavedDir()/TEXT("Verification/04-jump.png"),true,false); CapturePhase=8; }
        if(Age>18 && CapturePhase==8) { AI->SetManualIntent(EToyIntent::Bend); CapturePhase=9; }
        if(Age>19 && CapturePhase==9) { FScreenshotRequest::RequestScreenshot(FPaths::ProjectSavedDir()/TEXT("Verification/05-bend.png"),true,false); CapturePhase=10; }
        if(Age>21 && CapturePhase==10) { AI->SetManualIntent(EToyIntent::Crawl); CapturePhase=11; }
        if(Age>22 && CapturePhase==11) { FScreenshotRequest::RequestScreenshot(FPaths::ProjectSavedDir()/TEXT("Verification/06-crawl.png"),true,false); CapturePhase=12; }
        if(Age>24 && CapturePhase==12) { AI->SetManualIntent(EToyIntent::SwordSwing); CapturePhase=13; }
        if(Age>24.5 && CapturePhase==13) { FScreenshotRequest::RequestScreenshot(FPaths::ProjectSavedDir()/TEXT("Verification/07-sword.png"),true,false); CapturePhase=14; }
        if(Age>27) FPlatformMisc::RequestExit(false);
    }
    if(!bVerify || bFinished) return;
    if(Age>7 && Phase==0) { AI->ForceIntent(EToyIntent::LookAround); Phase=1; }
    if(Age>10 && Phase==1) { AI->ForceIntent(EToyIntent::Gesture); Phase=2; }
    if(Age>13 && Phase==2) { AI->ForceIntent(EToyIntent::Idle); Phase=3; }
    if(Age>16 && Phase==3) { AI->ForceIntent(EToyIntent::Wander); Phase=4; }
    if(Age>30 && Phase==4)
    {
        ArrivalsBeforeFailure=AI->Arrivals;
        AI->TestUnreachableDestination(); Phase=5;
        UE_LOG(LogTemp,Display,TEXT("TOY TEST injected unreachable path"));
    }
    if(Age>45 && Phase==5 && AI->Arrivals>ArrivalsBeforeFailure)
    {
        // A real collision obstacle invisible to nav, not a fake 'failed' callback.
        AI->ForceIntent(EToyIntent::Idle);
        Toy->SetIntent(EToyIntent::Wander);
        AI->RequestDestination(FVector(-600,-650,90));
        Phase=50;
    }
    if(Phase==50 && FVector::Dist2D(Toy->GetActorLocation(),FVector(-600,-650,90))<30 && AI->NavigationState!=EToyNavigationState::Moving)
    {
        AI->ForceIntent(EToyIntent::Idle);
        StuckStart=Toy->GetActorLocation();
        ArrivalsBeforeStuck=AI->Arrivals;
        TestBlocker=GetWorld()->SpawnActor<AStaticMeshActor>(StuckStart+FVector(80,0,0),FRotator::ZeroRotator);
        UStaticMeshComponent* Block=TestBlocker->GetStaticMeshComponent();
        Block->SetMobility(EComponentMobility::Movable);
        Block->SetStaticMesh(LoadObject<UStaticMesh>(nullptr,TEXT("/Engine/BasicShapes/Cube.Cube")));
        Block->SetWorldScale3D(FVector(.3f,20.f,3.f));
        Block->SetCollisionProfileName(TEXT("BlockAllDynamic"));
        Block->SetCanEverAffectNavigation(false);
        Toy->SetIntent(EToyIntent::Wander);
        AI->RequestDestination(StuckStart+FVector(220,0,0));
        Phase=6;
        UE_LOG(LogTemp,Display,TEXT("TOY TEST injected physical blocker"));
    }
    if(Phase==6)
    {
        // Wall near face is x=start+65, capsule radius=34.
        MaxWallPenetration=FMath::Max(MaxWallPenetration,static_cast<float>(Toy->GetActorLocation().X-StuckStart.X-31));
        if(AI->StuckRecoveries>0)
        {
            TestBlocker->Destroy(); TestBlocker=nullptr;
            Phase=7;
            UE_LOG(LogTemp,Display,TEXT("TOY TEST blocker removed after detected stuck state"));
        }
    }
    if(Age>85) FinishVerification();
}
void AToyGameMode::FinishVerification()
{
    bFinished=true;
    AToyAIController* AI=Cast<AToyAIController>(Toy->GetController());
    const bool Wandering=AI->Arrivals>=3;
    const bool FailedRecovery=(Phase==6 || Phase==7) && AI->Arrivals>ArrivalsBeforeFailure;
    const bool StuckRecovery=Phase==7 && AI->Arrivals>ArrivalsBeforeStuck;
    const bool Collisions=Toy->CollisionHits>0 && MaxWallPenetration<3 && Toy->StabilityViolations==0;
    const bool Motion=Toy->bUseImageCutout ?
        (Toy->bCutoutReady && Toy->CutoutMovingSamples>100 && Toy->MaxCutoutBob>0.1f && Toy->MaxCutoutBob<=2.51f
         && Toy->MaxCutoutLean<=10.01f && Toy->ForbiddenSimulatedBodies==0 && Toy->StabilityViolations==0
         && !Toy->bPhysicsReady && Toy->PerturbationCount==0) : Toy->bPhysicsReady && Toy->PerturbationCount>=3 && Toy->AnimationSamples>100 && Toy->MaxFootMotion>.01f
        && Toy->StabilityViolations==0 && Toy->ForbiddenSimulatedBodies==0 && Toy->JointSamples>100
        && Toy->MaxJointLimitExcessDegrees<10 && Toy->MaxLimbFrameRotationDegrees<15
        && Toy->MaxAppliedPerturbation<=20;
    // Raw post-solver angular speed is diagnostic; pose continuity and joint
    // excursion directly test the intended bounded secondary motion at 60 Hz.
    TSharedRef<FJsonObject> R=MakeShared<FJsonObject>();
    R->SetStringField(TEXT("engine"),FEngineVersion::Current().ToString());
    R->SetBoolField(TEXT("wandering_pass"),Wandering);
    R->SetBoolField(TEXT("failed_path_recovery_pass"),FailedRecovery);
    R->SetBoolField(TEXT("stuck_recovery_pass"),StuckRecovery);
    R->SetBoolField(TEXT("stable_collision_pass"),Collisions);
    R->SetBoolField(TEXT("motion_telemetry_pass"),Motion);
    R->SetStringField(TEXT("appearance_mode"),Toy->bUseImageCutout?TEXT("trunks_image_cutout"):TEXT("rigged_placeholder"));
    R->SetBoolField(TEXT("cutout_asset_ready"),Toy->bCutoutReady);
    R->SetNumberField(TEXT("cutout_direction_changes"),Toy->CutoutDirectionChanges);
    R->SetBoolField(TEXT("directional_flip_pass"),!Toy->bUseImageCutout || Toy->CutoutDirectionChanges>1);
    R->SetNumberField(TEXT("cutout_moving_samples"),Toy->CutoutMovingSamples);
    R->SetNumberField(TEXT("max_cutout_bob_cm"),Toy->MaxCutoutBob);
    R->SetNumberField(TEXT("max_cutout_lean_degrees"),Toy->MaxCutoutLean);
    R->SetNumberField(TEXT("arrivals"),AI->Arrivals);
    R->SetNumberField(TEXT("path_failures"),AI->PathFailures);
    R->SetNumberField(TEXT("stuck_recoveries"),AI->StuckRecoveries);
    R->SetNumberField(TEXT("capsule_wall_hits"),Toy->CollisionHits);
    R->SetNumberField(TEXT("max_wall_penetration_cm"),MaxWallPenetration);
    R->SetNumberField(TEXT("stability_violations"),Toy->StabilityViolations);
    R->SetNumberField(TEXT("max_limb_distance_cm"),Toy->MaxLimbDistance);
    R->SetNumberField(TEXT("max_body_angular_speed_rad_s"),Toy->MaxBodyAngularSpeed);
    R->SetNumberField(TEXT("max_joint_limit_excess_degrees"),Toy->MaxJointLimitExcessDegrees);
    R->SetNumberField(TEXT("max_limb_frame_rotation_degrees"),Toy->MaxLimbFrameRotationDegrees);
    R->SetNumberField(TEXT("max_applied_perturbation_cm_s"),Toy->MaxAppliedPerturbation);
    R->SetNumberField(TEXT("joint_samples"),Toy->JointSamples);
    R->SetNumberField(TEXT("forbidden_simulated_body_samples"),Toy->ForbiddenSimulatedBodies);
    R->SetNumberField(TEXT("perturbations"),Toy->PerturbationCount);
    R->SetNumberField(TEXT("animation_samples"),Toy->AnimationSamples);
    R->SetNumberField(TEXT("max_foot_frame_motion_cm"),Toy->MaxFootMotion);
    R->SetNumberField(TEXT("simulation_seconds"),Age);
    R->SetStringField(TEXT("visual_review"),TEXT("See Docs/VERIFICATION.md; telemetry alone does not establish aesthetic quality."));
    FString Json; auto Writer=TJsonWriterFactory<>::Create(&Json); FJsonSerializer::Serialize(R,Writer);
    const FString Directory=FPaths::ProjectSavedDir()/TEXT("Verification");
    IFileManager::Get().MakeDirectory(*Directory,true);
    FFileHelper::SaveStringToFile(Json,*(Directory/TEXT("runtime.json")));
    const bool Passed=Wandering&&FailedRecovery&&StuckRecovery&&Collisions&&Motion;
    UE_LOG(LogTemp,Display,TEXT("TOY VERIFICATION %s: %s"),Passed?TEXT("PASS"):TEXT("FAIL"),*Json);
    FPlatformMisc::RequestExitWithStatus(false,Passed?0:1);
}
void AToyHUD::DrawHUD()
{
    Super::DrawHUD();
    if(!Canvas) return;
    AToyGameMode* Mode=Cast<AToyGameMode>(UGameplayStatics::GetGameMode(GetWorld()));
    if(!Mode || !Mode->Toy) return;
    AToyCharacter* T=Mode->Toy;
    AToyAIController* AI=Cast<AToyAIController>(T->GetController());
    DrawRect(FLinearColor(.025,.032,.055,.9),22,22,505,268);
    DrawText(TEXT("AUTONOMOUS TOY LAB"),FLinearColor(.8,.7,1),38,34,nullptr,1.5f);
    DrawText(T->bUseImageCutout?TEXT("Trunks / 2D image cutout"):TEXT("Rigged mannequin placeholder / reference-inspired accents"),FLinearColor::White,38,66);
    DrawText(FString::Printf(TEXT("Intent: %s   |   speed: %.0f cm/s"),*UEnum::GetValueAsString(T->Intent),T->GetVelocity().Size2D()),FLinearColor::White,38,91);
    if(AI) DrawText(FString::Printf(TEXT("Arrivals %d    Recoveries %d    Perturbations %d"),AI->Arrivals,AI->PathFailures,T->PerturbationCount),FLinearColor(.55,.85,1),38,116);
    DrawText(AI && AI->bManualControl?TEXT("MANUAL - stays active until another command"):TEXT("AUTO - choosing actions"),FLinearColor(.8,.8,.8),38,146);
    const TCHAR* Names[]={TEXT("1 Stop"),TEXT("2 Wander"),TEXT("3 Look"),TEXT("4 Sway"),TEXT("0 Auto"),TEXT("5 Jump"),TEXT("6 Bend"),TEXT("7 Crawl"),TEXT("8 Sword")};
    for (int32 I=0;I<9;++I)
    {
        const float X=38+(I%5)*95;
        const float Y=174+(I/5)*40;
        DrawRect(FLinearColor(.16,.20,.27,1),X,Y,88,30);
        DrawText(Names[I],FLinearColor::White,X+7,Y+8);
        AddHitBox(FVector2D(X,Y),FVector2D(88,30),FName(*FString::FromInt(I==4?0:(I>4?I:I+1))),true);
    }
    DrawText(TEXT("Click a button, or click the game view then press 1-8 / 0."),FLinearColor(.8,.8,.8),38,258);
}
void AToyHUD::NotifyHitBoxClick(FName BoxName)
{
    Super::NotifyHitBoxClick(BoxName);
    if (AToyPlayerController* PC=Cast<AToyPlayerController>(GetOwningPlayerController()))
        PC->ToyAction(FCString::Atoi(*BoxName.ToString()));
}
