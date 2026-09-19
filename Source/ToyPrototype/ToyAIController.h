#pragma once
#include "CoreMinimal.h"
#include "AIController.h"
#include "Navigation/PathFollowingComponent.h"
#include "ToyCharacter.h"
#include "ToyAIController.generated.h"

UENUM(BlueprintType)
enum class EToyNavigationState : uint8 { Paused, Moving, Recovering };

UCLASS()
class TOYPROTOTYPE_API AToyAIController : public AAIController
{
    GENERATED_BODY()
public:
    virtual void OnPossess(APawn* Pawn) override;
    virtual void OnUnPossess() override;
    virtual void OnMoveCompleted(FAIRequestID RequestID, const FPathFollowingResult& Result) override;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Toy|Navigation") EToyNavigationState NavigationState = EToyNavigationState::Paused;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Toy|Verification") int32 Arrivals = 0;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Toy|Verification") int32 PathFailures = 0;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Toy|Verification") int32 StuckRecoveries = 0;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Toy|Verification") int32 MoveRequests = 0;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Toy|Verification") int32 NavSampleFailures = 0;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Toy|Verification") FVector Destination;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Toy|Verification") FVector HomeLocation;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Toy|Verification") FString LastEvent = TEXT("Starting");
    int32 IntentCounts[8] = {0,0,0,0};
    UFUNCTION(BlueprintCallable, Category="Toy|Debug") void ForceIntent(EToyIntent NewIntent);
    UFUNCTION(BlueprintCallable, Category="Toy|Debug") void TestUnreachableDestination();
    bool bManualControl = false;
    EToyIntent ManualIntent = EToyIntent::Idle;
    void SetManualIntent(EToyIntent NewIntent);
    void ResumeAutonomy();
    bool RequestDestination(const FVector& Goal);
private:
    FRandomStream IntentRandom;
    FRandomStream NavigationRandom;
    FTimerHandle ThinkTimer;
    float NextDecisionTime = 0;
    float MoveStarted = 0;
    float LastProgressTime = 0;
    FVector LastProgressLocation;
    FAIRequestID ActiveRequest;
    int32 ConsecutiveFailures = 0;
    bool bSuppressCompletion = false;
    bool bIssuingMove = false;
    UPROPERTY() TObjectPtr<AToyCharacter> Toy;
    void Think();
    void ChooseIntent();
    void EnterIntent(EToyIntent NewIntent);
    bool SampleReachableDestination(FVector& Out);
    void Pause(bool bRecovery);
    void Recover(const FString& Reason, bool bStuck = false);
};
