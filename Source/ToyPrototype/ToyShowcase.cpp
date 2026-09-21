#include "ToyArena.h"
#include "ToyCharacter.h"
#include "Camera/CameraActor.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Engine/World.h"
#include "UnrealClient.h"
#include "Misc/Paths.h"

void AToyArena::TickShowcase(float Dt)
{
 if(ShowcaseFrame>=450){FPlatformMisc::RequestExit(false);return;}
 const int32 F=FMath::Max(0,ShowcaseFrame);
 // A scripted presentation of the existing four clips, not autonomous combat.
 FVector Travel=FVector::ZeroVector;
 if(F>=60 && F<120)Travel=FVector(1,0,0);
 if(F>=255 && F<315)Travel=FVector(-1,0,0);
 if(ShowcaseFrame==120 || ShowcaseFrame==345)
 {
  FVector Dir=ShowcaseFrame==120?FVector(1,0,0):FVector(-1,0,0);
  Toy->LaunchCharacter(Dir*650+FVector(0,0,65),true,true);Toy->StartRigAction(2);
 }
 if(ShowcaseFrame==165 || ShowcaseFrame==210 || ShowcaseFrame==375)Toy->StartRigAction(1);
 if(!Travel.IsNearlyZero())Toy->AddMovementInput(Travel);
 const float DesiredYaw=Travel.IsNearlyZero()?-70.f:Travel.Rotation().Yaw;
 Toy->SetActorRotation(FMath::RInterpTo(Toy->GetActorRotation(),FRotator(0,DesiredYaw,0),Dt,9));
 // Low three-quarter view includes the kitchen beyond the character.
 const FVector Focus=Toy->GetActorLocation()+FVector(0,0,25);
 const float Orbit=FMath::Sin(float(F)/450.f*PI)*12.f;
 const FVector Offset=FVector(155,-380,185).RotateAngleAxis(Orbit,FVector::UpVector);
 Camera->SetActorLocation(Focus+Offset);
 Camera->SetActorRotation((Focus-Camera->GetActorLocation()).Rotation());
 if(ShowcaseFrame>=0)
  FScreenshotRequest::RequestScreenshot(ShowcaseDirectory/FString::Printf(TEXT("frame_%04d.png"),ShowcaseFrame),false,false);
 ++ShowcaseFrame;
}
