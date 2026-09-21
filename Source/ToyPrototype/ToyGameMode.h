#pragma once
#include "CoreMinimal.h"
#include "GameFramework/GameModeBase.h"
#include "GameFramework/HUD.h"
#include "ToyGameMode.generated.h"
UCLASS()
class TOYPROTOTYPE_API AToyHUD : public AHUD
{
    GENERATED_BODY()
public: virtual void DrawHUD() override;
 bool bControlsExpanded = true;
 void ToggleControls() { bControlsExpanded = !bControlsExpanded; }
 virtual void NotifyHitBoxClick(FName BoxName) override;
};
UCLASS()
class TOYPROTOTYPE_API AToyGameMode : public AGameModeBase
{
    GENERATED_BODY()
public:
    AToyGameMode();
    virtual void BeginPlay() override;
    virtual void Tick(float DeltaSeconds) override;
    UPROPERTY() TObjectPtr<class AToyCharacter> Toy;
    UPROPERTY() TObjectPtr<class AToyArena> Arena;
private:
    bool bVerify=false;
    bool bCapture=false;
    bool bMontage=false;
    int32 MontageFrame=-60;
    int32 MontageAction=-1;
    FString MontageDirectory;
    int32 CapturePhase=0;
    bool bFinished=false;
    int32 Phase=0;
    float Age=0;
    int32 ArrivalsBeforeFailure=0;
    int32 ArrivalsBeforeStuck=0;
    float MaxWallPenetration=0;
    FVector StuckStart;
    UPROPERTY() TObjectPtr<class AStaticMeshActor> TestBlocker;
    void FinishVerification();
};
