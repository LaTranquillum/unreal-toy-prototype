#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "ToyCharacter.generated.h"

UENUM(BlueprintType)
enum class EToyIntent : uint8 { Idle, Wander, LookAround, Gesture, Hop, Bend, Crawl, SwordSwing };

UCLASS()
class TOYPROTOTYPE_API AToyCharacter : public ACharacter
{
    GENERATED_BODY()
public:
    AToyCharacter();
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Toy|Appearance") bool bUseImageCutout = true;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Toy|Appearance", meta=(ClampMin="80",ClampMax="240")) float CutoutHeight = 180;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Toy|Components") TObjectPtr<class UStaticMeshComponent> ImageCutout;
    bool bCutoutReady = false;
    bool bRiggedBlockoutReady = false;
    int32 RigAction=0;
    float RigActionStarted=-100;
    bool EnableRiggedBlockout();
    void StartRigAction(int32 Action);
    int32 CutoutMovingSamples = 0;
    float MaxCutoutBob = 0;
    float MaxCutoutLean = 0;
    bool bCutoutFacesRight = false;
    int32 CutoutDirectionChanges = 0;
    int32 LookTurnCount = 0;
    bool bActionArtReady = false;
    int32 CurrentActionFrame = -1;
    int32 SwordFrameMask = 0;
    float JumpStartZ = 0;
    float MaxJumpRise = 0;
    UPROPERTY() TObjectPtr<class UMaterialInterface> StandingMaterial;
    UPROPERTY() TArray<TObjectPtr<class UMaterialInterface>> ActionMaterials;
    virtual void BeginPlay() override;
    virtual void Tick(float DeltaSeconds) override;
    virtual void EndPlay(const EEndPlayReason::Type Reason) override;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Toy|Intent") int32 BehaviorSeed = 2409;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Toy|Navigation", meta=(ClampMin="100", ClampMax="1500", Units="cm")) float WanderRadius = 650;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Toy|Intent", meta=(ClampMin="0.3", ClampMax="20", Units="s")) float PauseMin = 1.2f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Toy|Intent", meta=(ClampMin="0.3", ClampMax="20", Units="s")) float PauseMax = 3.5f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Toy|Intent", meta=(ClampMin="0")) float IdleWeight = 1;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Toy|Intent", meta=(ClampMin="0")) float WanderWeight = 5;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Toy|Intent", meta=(ClampMin="0")) float LookWeight = 1.5f;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Toy|Intent", meta=(ClampMin="0")) float GestureWeight = 1;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Toy|Motion", meta=(ClampMin="60", ClampMax="240", Units="cm/s")) float WalkSpeed = 150;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Toy|Physics", meta=(ClampMin="100", ClampMax="3000")) float DriveStrength = 800;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Toy|Physics", meta=(ClampMin="10", ClampMax="300")) float DriveDamping = 140;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Toy|Physics", meta=(ClampMin="1", ClampMax="20")) float BodyDamping = 10;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Toy|Physics", meta=(ClampMin="0", ClampMax="20", Units="cm/s")) float PerturbationIntensity = 8;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Toy|Physics") bool bEnableSecondaryPhysics = true;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Toy|State") EToyIntent Intent = EToyIntent::Idle;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Toy|State") bool bPhysicsReady = false;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Toy|State") int32 PerturbationCount = 0;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Toy|State") int32 CollisionHits = 0;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Toy|State") float MaxLimbDistance = 0;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Toy|State") float MaxBodyAngularSpeed = 0;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Toy|State") int32 StabilityViolations = 0;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Toy|State") int32 AnimationSamples = 0;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Toy|State") float MaxFootMotion = 0;
    float MaxJointLimitExcessDegrees = 0;
    float MaxLimbFrameRotationDegrees = 0;
    float MaxAppliedPerturbation = 0;
    int32 JointSamples = 0;
    int32 ForbiddenSimulatedBodies = 0;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Toy|Components") TObjectPtr<class UPhysicalAnimationComponent> PhysicalAnimation;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Toy|Components") TObjectPtr<class UTextRenderComponent> PlaceholderLabel;

    UFUNCTION(BlueprintCallable, Category="Toy|Physics") void ApplyToyPhysicsSettings();
    UFUNCTION(BlueprintCallable, Category="Toy|Physics") void PerturbOnce();
    void SetIntent(EToyIntent NewIntent);
    float IntentAge() const;
    const TArray<FName>& SecondaryBodies() const { return SimulatedBodies; }
private:
    FRandomStream MotionRandom;
    FTimerHandle PerturbTimer;
    FTimerHandle PhysicsInitTimer;
    TArray<FName> SimulatedBodies;
    UPROPERTY() TArray<TObjectPtr<class UStaticMeshComponent>> AccentParts;
    float IntentStarted = 0;
    FVector PreviousFoot = FVector::ZeroVector;
    bool bPreviousFootValid = false;
    TMap<FName,FQuat> PreviousLimbRotations;
    void SchedulePerturbation();
    UFUNCTION() void CapsuleHit(UPrimitiveComponent* HitComp, AActor* Other, UPrimitiveComponent* OtherComp, FVector NormalImpulse, const FHitResult& Hit);
};
