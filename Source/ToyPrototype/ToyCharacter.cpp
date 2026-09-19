#include "ToyCharacter.h"
#include "Camera/PlayerCameraManager.h"
#include "Engine/World.h"
#include "ToyAIController.h"
#include "ToyAnimInstance.h"
#include "Components/CapsuleComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Components/TextRenderComponent.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "PhysicsEngine/PhysicalAnimationComponent.h"
#include "PhysicsEngine/PhysicsAsset.h"
#include "PhysicsEngine/BodyInstance.h"
#include "PhysicsEngine/SkeletalBodySetup.h"
#include "PhysicsEngine/ConstraintInstance.h"
#include "Engine/SkeletalMesh.h"
#include "Materials/MaterialInterface.h"
#include "UObject/ConstructorHelpers.h"
#include "TimerManager.h"

AToyCharacter::AToyCharacter()
{
    PrimaryActorTick.bCanEverTick=true;
    GetCapsuleComponent()->InitCapsuleSize(34,88);
    GetCapsuleComponent()->SetNotifyRigidBodyCollision(true);
    GetCapsuleComponent()->OnComponentHit.AddDynamic(this,&AToyCharacter::CapsuleHit);
    GetCharacterMovement()->bOrientRotationToMovement=true;
    GetCharacterMovement()->RotationRate=FRotator(0,240,0);
    GetCharacterMovement()->MaxWalkSpeed=150;
    GetCharacterMovement()->MaxAcceleration=450;
    GetCharacterMovement()->BrakingDecelerationWalking=650;
    GetCharacterMovement()->bEnablePhysicsInteraction=false;
    GetCharacterMovement()->GetNavAgentPropertiesRef().AgentRadius=34;
    GetCharacterMovement()->GetNavAgentPropertiesRef().AgentHeight=176;
    bUseControllerRotationYaw=false;
    AIControllerClass=AToyAIController::StaticClass();
    AutoPossessAI=EAutoPossessAI::PlacedInWorldOrSpawned;
    static ConstructorHelpers::FObjectFinder<USkeletalMesh> MeshAsset(TEXT("/Game/Mannequin/Character/Mesh/SK_Mannequin.SK_Mannequin"));
    GetMesh()->SetSkeletalMeshAsset(MeshAsset.Object);
    GetMesh()->SetRelativeLocationAndRotation(FVector(0,0,-88),FRotator(0,-90,0));
    GetMesh()->SetAnimInstanceClass(UToyAnimInstance::StaticClass());
    GetMesh()->SetCollisionEnabled(ECollisionEnabled::QueryAndPhysics);
    GetMesh()->SetCollisionObjectType(ECC_PhysicsBody);
    GetMesh()->SetCollisionResponseToAllChannels(ECR_Ignore);
    // Capsule is the sole scene collider in this first prototype.
    // Secondary arm simulation is isolated from scene-contact conflicts.
    GetMesh()->SetCanEverAffectNavigation(false);
    GetMesh()->VisibilityBasedAnimTickOption=EVisibilityBasedAnimTickOption::AlwaysTickPoseAndRefreshBones;
    GetMesh()->bEnableUpdateRateOptimizations=false;
    PhysicalAnimation=CreateDefaultSubobject<UPhysicalAnimationComponent>(TEXT("SecondaryLimbDrives"));
    PlaceholderLabel=CreateDefaultSubobject<UTextRenderComponent>(TEXT("PlaceholderLabel"));
    PlaceholderLabel->SetupAttachment(RootComponent);
    PlaceholderLabel->SetRelativeLocation(FVector(0,0,130));
    PlaceholderLabel->SetText(FText::FromString(TEXT("RIGGED PLACEHOLDER")));
    PlaceholderLabel->SetWorldSize(15);
    PlaceholderLabel->SetHorizontalAlignment(EHTA_Center);
    PlaceholderLabel->SetTextRenderColor(FColor(183,151,245));
    PlaceholderLabel->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    static ConstructorHelpers::FObjectFinder<UStaticMesh> Sphere(TEXT("/Engine/BasicShapes/Sphere.Sphere"));
    static ConstructorHelpers::FObjectFinder<UStaticMesh> Cube(TEXT("/Engine/BasicShapes/Cube.Cube"));
    static ConstructorHelpers::FObjectFinder<UStaticMesh> Plane(TEXT("/Engine/BasicShapes/Plane.Plane"));
    ImageCutout=CreateDefaultSubobject<UStaticMeshComponent>(TEXT("TrunksImageCutout"));
    ImageCutout->SetupAttachment(RootComponent);
    ImageCutout->SetStaticMesh(Plane.Object);
    ImageCutout->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    ImageCutout->SetCanEverAffectNavigation(false);
    ImageCutout->SetCastShadow(false);
    ImageCutout->SetVisibility(false);
    // Explicit blockout accents, not a reference-matching model. No extra collision.
    auto Part=[&](const TCHAR* Name,FName Bone,UStaticMesh* Shape,FVector Location,FVector Scale,FRotator Rotation)
    {
        UStaticMeshComponent* Comp=CreateDefaultSubobject<UStaticMeshComponent>(Name);
        Comp->SetupAttachment(GetMesh(),Bone); Comp->SetStaticMesh(Shape);
        Comp->SetRelativeLocationAndRotation(Location,Rotation); Comp->SetRelativeScale3D(Scale);
        Comp->SetCollisionEnabled(ECollisionEnabled::NoCollision); Comp->SetCanEverAffectNavigation(false);
        AccentParts.Add(Comp);
    };
    Part(TEXT("PurpleHairBlockout"),TEXT("head"),Sphere.Object,FVector(6,0,0),FVector(.25,.28,.24),FRotator::ZeroRotator);
    Part(TEXT("GoldBackScabbardBlockout"),TEXT("spine_03"),Cube.Object,FVector(-4.440907,-12.633511,1.748572),FVector(.07,.08,.75),FRotator(-70.754419,-89.963349,105.255321));
}

void AToyCharacter::BeginPlay()
{
    Super::BeginPlay();
    MotionRandom.Initialize(BehaviorSeed ^ 0x7c17);
    GetMesh()->SetCollisionResponseToAllChannels(ECR_Ignore);
    GetCharacterMovement()->MaxWalkSpeed=FMath::Clamp(WalkSpeed,60.f,240.f);
    GetMesh()->SetMaterial(0,LoadObject<UMaterialInterface>(nullptr,TEXT("/Game/Toy/Materials/M_Blue.M_Blue")));
    GetMesh()->SetMaterial(1,LoadObject<UMaterialInterface>(nullptr,TEXT("/Game/Toy/Materials/M_Dark.M_Dark")));
    AccentParts[0]->SetMaterial(0,LoadObject<UMaterialInterface>(nullptr,TEXT("/Game/Toy/Materials/M_Purple.M_Purple")));
    AccentParts[1]->SetMaterial(0,LoadObject<UMaterialInterface>(nullptr,TEXT("/Game/Toy/Materials/M_Gold.M_Gold")));
    if (bUseImageCutout)
    {
        UMaterialInterface* Material=LoadObject<UMaterialInterface>(nullptr,TEXT("/Game/Toy/Cutout/M_TrunksCutout.M_TrunksCutout"));
        bCutoutReady=Material!=nullptr;
        StandingMaterial=Material;
        bActionArtReady=true;
        for(int32 I=0;I<6;++I)
        {
            UMaterialInterface* Pose=LoadObject<UMaterialInterface>(nullptr,*FString::Printf(TEXT("/Game/Toy/Actions/M_Action%d.M_Action%d"),I,I));
            ActionMaterials.Add(Pose);bActionArtReady&=Pose!=nullptr;
        }
        ImageCutout->SetMaterial(0,Material);
        ImageCutout->SetVisibility(bCutoutReady);
        ImageCutout->SetHiddenInGame(false);
        GetMesh()->SetVisibility(false,true);
        GetMesh()->SetHiddenInGame(true,true);
        GetMesh()->SetAllBodiesSimulatePhysics(false);
        GetMesh()->SetComponentTickEnabled(false);
        bEnableSecondaryPhysics=false;
        PlaceholderLabel->SetText(FText::FromString(bCutoutReady?TEXT("TRUNKS - IMAGE CUTOUT"):TEXT("MISSING TRUNKS IMAGE MATERIAL")));
        UE_LOG(LogTemp,Display,TEXT("TOY cutout ready=%d; skeletal animation and limb physics disabled"),bCutoutReady);
        return;
    }
    ImageCutout->SetVisibility(false);
    // Allow the first animated pose to settle before creating physical-animation motors.
    GetWorldTimerManager().SetTimer(PhysicsInitTimer,this,&AToyCharacter::ApplyToyPhysicsSettings,.5f,false);
    SchedulePerturbation();
    if (!GetMesh()->GetSkeletalMeshAsset() || !GetMesh()->GetAnimInstance())
        PlaceholderLabel->SetText(FText::FromString(TEXT("MISSING RIG / ANIMATION")));
}

void AToyCharacter::ApplyToyPhysicsSettings()
{
    USkeletalMeshComponent* Mesh=GetMesh();
    Mesh->SetAllBodiesSimulatePhysics(false);
    SimulatedBodies.Reset(); bPhysicsReady=false;
    PhysicalAnimation->SetSkeletalMeshComponent(Mesh);
    if (bUseImageCutout || !bEnableSecondaryPhysics || !Mesh->GetPhysicsAsset()) return;
    FPhysicalAnimationData Drive;
    Drive.bIsLocalSimulation=true;
    Drive.OrientationStrength=FMath::Clamp(DriveStrength,100.f,3000.f);
    Drive.AngularVelocityStrength=FMath::Clamp(DriveDamping,10.f,300.f);
    Drive.PositionStrength=0; Drive.VelocityStrength=0;
    Drive.MaxLinearForce=0; Drive.MaxAngularForce=5000;
    const FName Selected[]={TEXT("lowerarm_l"),TEXT("hand_l"),TEXT("lowerarm_r"),TEXT("hand_r")};
    for (FName Name:Selected)
    {
        // No body-name fallback: never accidentally simulate pelvis/root or a parent.
        if (Mesh->GetPhysicsAsset()->FindBodyIndex(Name)==INDEX_NONE) continue;
        FBodyInstance* Body=Mesh->GetBodyInstance(Name);
        if (!Body || !Body->IsValidBodyInstance()) continue;
        Body->LinearDamping=2;
        Body->AngularDamping=FMath::Clamp(BodyDamping,1.f,20.f);
        Body->UpdateDampingProperties();
        
        PhysicalAnimation->ApplyPhysicalAnimationSettings(Name,Drive);
        Body->SetInstanceSimulatePhysics(true);
        Body->SetMaxAngularVelocityInRadians(3,false);
        Body->SetAngularVelocityInRadians(FVector::ZeroVector,false);
        Body->PhysicsBlendWeight=.65f;
        SimulatedBodies.Add(Name);
    }
    // Modify this component's live constraints, leaving the source template asset intact.
    for (FConstraintInstance* Joint:Mesh->Constraints)
    {
        if (!Joint || !SimulatedBodies.Contains(Joint->GetChildBoneName())) continue;
        Joint->SetDisableCollision(true);
        Joint->SetLinearLimits(LCM_Locked,LCM_Locked,LCM_Locked,0);
        Joint->SetAngularSwing1Limit(ACM_Limited,55);
        Joint->SetAngularSwing2Limit(ACM_Limited,35);
        Joint->SetAngularTwistLimit(ACM_Limited,35);
        Joint->SetProjectionParams(true,.2f,.2f,3.f,15.f);
    }
    bPhysicsReady=SimulatedBodies.Num()==4;
    UE_LOG(LogTemp,Display,TEXT("TOY physics: %d selected arm bodies; capsule/pelvis/legs kinematic"),SimulatedBodies.Num());
}

void AToyCharacter::SchedulePerturbation()
{
    GetWorldTimerManager().SetTimer(PerturbTimer,[this]() { PerturbOnce(); SchedulePerturbation(); },MotionRandom.FRandRange(3.f,7.f),false);
}

void AToyCharacter::PerturbOnce()
{
    if (bUseImageCutout || !bEnableSecondaryPhysics || !bPhysicsReady || SimulatedBodies.IsEmpty() || PerturbationIntensity<=0) return;
    const FName Body=SimulatedBodies[MotionRandom.RandRange(0,SimulatedBodies.Num()-1)];
    const FVector Direction=MotionRandom.VRand();
    // A single bounded velocity change in cm/s, on a selected upper-body body only.
    GetMesh()->AddImpulse(Direction*FMath::Clamp(PerturbationIntensity,0.f,20.f),Body,true);
    MaxAppliedPerturbation=FMath::Max(MaxAppliedPerturbation,FMath::Clamp(PerturbationIntensity,0.f,20.f));
    ++PerturbationCount;
}

void AToyCharacter::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);
    if (APlayerController* PC=GetWorld()->GetFirstPlayerController())
    {
        if (PC->PlayerCameraManager)
            PlaceholderLabel->SetWorldRotation((PC->PlayerCameraManager->GetCameraLocation()-PlaceholderLabel->GetComponentLocation()).Rotation());
    }
    if (GetActorLocation().ContainsNaN() || GetActorLocation().Z < -50 || FMath::Abs(GetActorRotation().Roll)>1 || FMath::Abs(GetActorRotation().Pitch)>1)
        ++StabilityViolations;
    if (bUseImageCutout)
    {
        if (APlayerController* PC=GetWorld()->GetFirstPlayerController())
        {
            if (PC->PlayerCameraManager)
            {
                const FVector ToCamera=(PC->PlayerCameraManager->GetCameraLocation()-GetActorLocation()).GetSafeNormal();
                const FVector Right=FRotationMatrix(PC->PlayerCameraManager->GetCameraRotation()).GetUnitAxis(EAxis::Y);
                const FQuat Facing=FRotationMatrix::MakeFromXZ(Right,-ToCamera).ToQuat();
                const FVector Up=Facing.GetAxisY();
                // Screen-space direction with a dead zone; keep facing while paused.
                const float SideSpeed=FVector::DotProduct(GetVelocity(),Right);
                if (FMath::Abs(SideSpeed)>15.f)
                {
                    const bool FacesRight=SideSpeed>0;
                    if (FacesRight!=bCutoutFacesRight) ++CutoutDirectionChanges;
                    bCutoutFacesRight=FacesRight;
                }
                if (Intent==EToyIntent::LookAround)
                {
                    const bool LookRight=(FMath::FloorToInt(IntentAge()/1.0f)%2)!=0;
                    if (LookRight!=bCutoutFacesRight) ++LookTurnCount;
                    bCutoutFacesRight=LookRight;
                }
                const float Moving=FMath::Clamp(static_cast<float>(GetVelocity().Size2D())/150.f,0.f,1.f);
                const float T=GetWorld()->GetTimeSeconds();
                const float Bob=2.5f*Moving*FMath::Abs(FMath::Sin(T*7.f));
                const float Lean=2.f*Moving*FMath::Sin(T*7.f)+(Intent==EToyIntent::Gesture?8.f*FMath::Sin(IntentAge()*4.f):0.f);
                int32 Frame=-1;
                if(Intent==EToyIntent::Bend) Frame=IntentAge()<.35f?0:3;
                if(Intent==EToyIntent::Crawl) Frame=(FMath::FloorToInt(IntentAge()*3.f)%2)==0?1:4;
                if(Intent==EToyIntent::SwordSwing) {Frame=(FMath::FloorToInt(IntentAge()*3.f)%2)==0?2:5;SwordFrameMask|=Frame==2?1:2;}
                if(!bActionArtReady) Frame=-1;
                if(Frame!=CurrentActionFrame)
                {
                    ImageCutout->SetMaterial(0,Frame<0?StandingMaterial.Get():ActionMaterials[Frame].Get());
                    CurrentActionFrame=Frame;
                }
                if(Intent==EToyIntent::Hop) MaxJumpRise=FMath::Max(MaxJumpRise,static_cast<float>(GetActorLocation().Z-JumpStartZ));
                const float Height=FMath::Clamp(CutoutHeight,80.f,240.f);
                const float Aspect=Frame<0?(1031.f/1525.f):1.f;
                const float Baselines[]={.98f,.98f,.98f,.81f,.81f,.87f};
                const float Baseline=Frame<0?.985f:Baselines[Frame];
                ImageCutout->SetWorldScale3D(FVector((bCutoutFacesRight?-1.f:1.f)*Height*Aspect/100.f,Height/100.f,1));
                ImageCutout->SetWorldLocation(GetActorLocation()-FVector(0,0,88)+Up*(Height*(Baseline-.5f))+FVector(0,0,Bob));
                ImageCutout->SetWorldRotation(FQuat(ToCamera,FMath::DegreesToRadians(Lean))*Facing);
                MaxCutoutBob=FMath::Max(MaxCutoutBob,Bob);
                MaxCutoutLean=FMath::Max(MaxCutoutLean,FMath::Abs(Lean));
                if (Moving>.2f) ++CutoutMovingSamples;
                if (ImageCutout->GetComponentLocation().ContainsNaN()) ++StabilityViolations;
            }
        }
        for (const FBodyInstance* Body:GetMesh()->Bodies)
            if (Body && Body->IsInstanceSimulatingPhysics()) ++ForbiddenSimulatedBodies;
        return;
    }
    for (FName Name:SimulatedBodies)
    {
        const FQuat Rotation=GetMesh()->GetBoneQuaternion(Name,EBoneSpaces::ComponentSpace);
        if (const FQuat* Previous=PreviousLimbRotations.Find(Name))
            MaxLimbFrameRotationDegrees=FMath::Max(MaxLimbFrameRotationDegrees,static_cast<float>(FMath::RadiansToDegrees(Previous->AngularDistance(Rotation))));
        PreviousLimbRotations.Add(Name,Rotation);
        const FVector Position=GetMesh()->GetBoneLocation(Name);
        const float Distance=FVector::Dist(Position,GetActorLocation());
        MaxLimbDistance=FMath::Max(MaxLimbDistance,Distance);
        const FBodyInstance* Body=GetMesh()->GetBodyInstance(Name);
        if (Body)
        {
            const float AngularSpeed=Body->GetUnrealWorldAngularVelocityInRadians().Size();
            if (AngularSpeed>MaxBodyAngularSpeed && AngularSpeed>7)
                UE_LOG(LogTemp,Display,TEXT("TOY angular peak: %s %.2f rad/s at t=%.3f intent=%d"),*Name.ToString(),AngularSpeed,GetWorld()->GetTimeSeconds(),static_cast<int>(Intent));
            MaxBodyAngularSpeed=FMath::Max(MaxBodyAngularSpeed,AngularSpeed);
        }
        if (Position.ContainsNaN() || Distance>180) ++StabilityViolations;
    }
    for (FConstraintInstance* Joint:GetMesh()->Constraints)
    {
        if (!Joint || !SimulatedBodies.Contains(Joint->GetChildBoneName())) continue;
        // Engine GetCurrent* returns radians; configured limits are degrees.
        const float Excess=FMath::Max3(
            FMath::Abs(FMath::RadiansToDegrees(Joint->GetCurrentSwing1()))-Joint->GetAngularSwing1Limit(),
            FMath::Abs(FMath::RadiansToDegrees(Joint->GetCurrentSwing2()))-Joint->GetAngularSwing2Limit(),
            FMath::Abs(FMath::RadiansToDegrees(Joint->GetCurrentTwist()))-Joint->GetAngularTwistLimit());
        if (!FMath::IsFinite(Excess)) ++StabilityViolations;
        else MaxJointLimitExcessDegrees=FMath::Max(MaxJointLimitExcessDegrees,Excess);
        ++JointSamples;
    }
    if (bPhysicsReady)
    {
        for (const FBodyInstance* Body:GetMesh()->Bodies)
            if (Body && Body->IsInstanceSimulatingPhysics() && !SimulatedBodies.Contains(Body->BodySetup.Get()->BoneName)) ++ForbiddenSimulatedBodies;
    }
    const FVector Foot=GetMesh()->GetBoneTransform(GetMesh()->GetBoneIndex(TEXT("foot_l")),FTransform::Identity).GetLocation();
    if (GetVelocity().Size2D()>40)
    {
        if (bPreviousFootValid) MaxFootMotion=FMath::Max(MaxFootMotion,static_cast<float>(FVector::Dist(Foot,PreviousFoot)));
        ++AnimationSamples;
    }
    PreviousFoot=Foot;
    bPreviousFootValid=true;
}

void AToyCharacter::CapsuleHit(UPrimitiveComponent*,AActor* Other,UPrimitiveComponent*,FVector,const FHitResult& Hit)
{
    if (Other && Other!=this && FMath::Abs(Hit.Normal.Z)<.5f) ++CollisionHits;
}
void AToyCharacter::SetIntent(EToyIntent NewIntent) { Intent=NewIntent; IntentStarted=GetWorld()->GetTimeSeconds(); }
float AToyCharacter::IntentAge() const { return GetWorld()->GetTimeSeconds()-IntentStarted; }
void AToyCharacter::EndPlay(const EEndPlayReason::Type Reason)
{
    GetWorldTimerManager().ClearTimer(PerturbTimer);
    GetWorldTimerManager().ClearTimer(PhysicsInitTimer);
    Super::EndPlay(Reason);
}
