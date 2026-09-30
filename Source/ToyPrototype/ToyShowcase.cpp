#include "ToyArena.h"
#include "ToyCharacter.h"
#include "ToyBlockoutAnim.h"
#include "Components/SkeletalMeshComponent.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "Misc/FileHelper.h"
#include "Camera/CameraActor.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Engine/World.h"
#include "UnrealClient.h"
#include "Misc/Paths.h"

void AToyArena::TickShowcase(float Dt)
{
 const bool bUpperPreview=FParse::Param(FCommandLine::Get(),TEXT("ToyUpperBodyPreview"));
 if(bUpperPreview)
 {
  if(ShowcaseFrame>=120){FPlatformMisc::RequestExit(false);return;}
  if(ShowcaseFrame==30 || ShowcaseFrame==75)Toy->StartRigAction(1);
  Toy->SetActorRotation(FRotator(0,-70,0));
  const FVector Focus=Toy->GetActorLocation()+FVector(0,0,35);
  const FVector Offset=Toy->GetActorForwardVector()*290+Toy->GetActorRightVector()*90+FVector(0,0,40);
  Camera->SetActorLocation(Focus+Offset);Camera->SetActorRotation((Focus-Camera->GetActorLocation()).Rotation());
  if(ShowcaseFrame>=0)
   FScreenshotRequest::RequestScreenshot(ShowcaseDirectory/FString::Printf(TEXT("upper_%04d.png"),ShowcaseFrame),false,false);
  if(ShowcaseFrame==20 || ShowcaseFrame==37 || ShowcaseFrame==65)
  {
   const bool Fingers=Toy->GetMesh()->GetBoneIndex(TEXT("index_3_r"))!=INDEX_NONE && Toy->GetMesh()->GetBoneIndex(TEXT("thumb_2_l"))!=INDEX_NONE;
   const bool Capsule=!Toy->GetMesh()->IsSimulatingPhysics() && Toy->GetMesh()->GetCollisionEnabled()==ECollisionEnabled::NoCollision;
   auto* Anim=Cast<UToyBlockoutAnim>(Toy->GetMesh()->GetAnimInstance());
   const bool Expression=Anim && (ShowcaseFrame==37?Anim->ShoutWeight>.5f:Anim->ShoutWeight<.1f);
   const FString Report=FString::Printf(TEXT("frame=%d finger_bones=%d capsule_authority=%d expression=%d passed=%d\n"),ShowcaseFrame,Fingers,Capsule,Expression,Fingers && Capsule && Expression);
   FFileHelper::SaveStringToFile(Report,*(ShowcaseDirectory/FString::Printf(TEXT("upper_%04d.txt"),ShowcaseFrame)));
  }
  ++ShowcaseFrame;return;
 }
 const bool bHeadPreview=FParse::Param(FCommandLine::Get(),TEXT("ToyHeadPreview"));
 if(ShowcaseFrame>=(bHeadPreview?205:450)){FPlatformMisc::RequestExit(false);return;}
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
 if(bHeadPreview)
 {
  const FVector Head=Toy->GetMesh()->GetSocketLocation(TEXT("head"))+FVector(0,0,15);
  const FVector Facing=Toy->GetActorForwardVector();
  const FVector Side=Toy->GetActorRightVector();
  Camera->SetActorLocation(Head+Facing*95+Side*18+FVector(0,0,4));
  Camera->SetActorRotation((Head-Camera->GetActorLocation()).Rotation());
  // Record the first natural blink at full closure, independent of warm-up length.
  static bool bCapturedBlink=false;
  auto* FaceAnim=Cast<UToyBlockoutAnim>(Toy->GetMesh()->GetAnimInstance());
  if(!bCapturedBlink && ShowcaseFrame>=0 && FaceAnim && FaceAnim->BlinkWeight>.9999f)
  {
   bCapturedBlink=true;
   FScreenshotRequest::RequestScreenshot(ShowcaseDirectory/TEXT("head_blink_closed.png"),false,false);
   const bool HasBlink=Toy->GetMesh()->FindMorphTarget(TEXT("Blink"))!=nullptr;
   const FString BlinkReport=FString::Printf(TEXT("blink=%.3f target=%d passed=%d\n"),FaceAnim->BlinkWeight,HasBlink,HasBlink);
   FFileHelper::SaveStringToFile(BlinkReport,*(ShowcaseDirectory/TEXT("head_blink_closed.txt")));
  }
  if(F==20 || F==90 || F==172 || F==200)
  {
   FScreenshotRequest::RequestScreenshot(ShowcaseDirectory/FString::Printf(TEXT("head_%03d.png"),F),false,false);
   auto* Anim=Cast<UToyBlockoutAnim>(Toy->GetMesh()->GetAnimInstance());
   const bool HasTargets=Toy->GetMesh()->FindMorphTarget(TEXT("Focused")) && Toy->GetMesh()->FindMorphTarget(TEXT("Shout"));
   const bool Correct=Anim && HasTargets && (F==90 ? Anim->FocusedWeight>.7f : F==172 ? Anim->ShoutWeight>.5f : Anim->FocusedWeight<.1f && Anim->ShoutWeight<.1f);
   const FString Row=FString::Printf(TEXT("frame=%d focused=%.3f shout=%.3f targets=%d passed=%d\n"),F,Anim?Anim->FocusedWeight:-1.f,Anim?Anim->ShoutWeight:-1.f,HasTargets,Correct);
   FFileHelper::SaveStringToFile(Row,*(ShowcaseDirectory/FString::Printf(TEXT("head_%03d.txt"),F)));
  }
 }
 else if(ShowcaseFrame>=0)
  FScreenshotRequest::RequestScreenshot(ShowcaseDirectory/FString::Printf(TEXT("frame_%04d.png"),ShowcaseFrame),false,false);
 ++ShowcaseFrame;
}
