#pragma once
#include "CoreMinimal.h"
#include "GameFramework/PlayerController.h"
#include "ToyPlayerController.generated.h"
UCLASS()
class TOYPROTOTYPE_API AToyPlayerController : public APlayerController
{
 GENERATED_BODY()
public:
 virtual void BeginPlay() override;
 virtual void SetupInputComponent() override;
 UFUNCTION(Exec) void ToyAction(int32 Action);
 int32 CommandsReceived[9]={0,0,0,0,0,0,0,0,0};
private:
 void Idle(); void Wander(); void Look(); void Sway(); void Auto();
 void Hop(); void Bend(); void Crawl(); void Sword();
 void FailedPath(); void Impulse(); void ToggleControls();
};
