#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "ToyArena.generated.h"

// Small, local, single-player combat slice. Capsule movement remains authoritative.
UCLASS()
class TOYPROTOTYPE_API AToyArena : public AActor
{
 GENERATED_BODY()
public:
 AToyArena();
 virtual void BeginPlay() override;
 virtual void Tick(float DeltaSeconds) override;
 void Attack();
 void Dodge();
 void Restart();
 void DamagePlayer(float Amount);
 void Draw(class AToyHUD* HUD, class UCanvas* Canvas);
 bool IsPlaying() const { return Remaining>0 && Health>0; }
 UPROPERTY() TObjectPtr<class AToyCharacter> Toy;
 UPROPERTY() TObjectPtr<class AStaticMeshActor> Drone;
 UPROPERTY() TObjectPtr<class AStaticMeshActor> Pickup;
 UPROPERTY() TObjectPtr<class ACameraActor> Camera;
 FVector Aim=FVector(0,1,0), MoveDirection=FVector::ZeroVector;
 float Health=100, Remaining=60, DroneHealth=100;
 int32 Score=0;
private:
 struct FBolt { TWeakObjectPtr<AStaticMeshActor> Actor; FVector Velocity; float Life=0; };
 TArray<FBolt> Bolts;
 float Clock=0, Swing=-1, DodgeUntil=0, DodgeReady=0, InvulnerableUntil=0;
 float ShootAt=2, RespawnAt=0, PickupAt=0, HitFlash=0, Shake=0;
 FVector LockedShot=FVector::ZeroVector;
 bool bTelegraph=false, bHitThisSwing=false, bVerify=false;
 int32 VerifyStage=0, Hits=0, Shots=0, DamageEvents=0, Dodges=0, Collected=0;
 TMap<FString,bool> Checks;
 FVector TestStart;
 float TestAge=0;
 class AStaticMeshActor* Shape(FVector Position,FVector Scale,const TCHAR* Mesh,const TCHAR* Material,bool Collision=false);
 void SpawnDrone();
 void UpdateDrone(float DeltaSeconds);
 void UpdateBolts(float DeltaSeconds);
 void Impact(FVector Position,bool bEnemy);
 void Tone(float Frequency,float Duration,float Volume);
 void Verify(float DeltaSeconds);
 void FinishVerify();
};
