#include "ToyArena.h"
#include "ToyCharacter.h"
#include "ToyGameMode.h"
#include "ToyPlayerController.h"
#include "Camera/CameraActor.h"
#include "Camera/CameraComponent.h"
#include "Camera/PlayerCameraManager.h"
#include "Components/CapsuleComponent.h"
#include "Components/SkeletalMeshComponent.h"
#if WITH_EDITOR
#include "ShaderCompiler.h"
#endif
#include "Components/AudioComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Components/TextRenderComponent.h"
#include "Engine/StaticMeshActor.h"
#include "Engine/StaticMesh.h"
#include "Engine/Canvas.h"
#include "EngineUtils.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Kismet/GameplayStatics.h"
#include "Sound/SoundWaveProcedural.h"
#include "DrawDebugHelpers.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "Misc/Paths.h"
#include "Misc/FileHelper.h"
#include "Misc/App.h"
#include "HAL/FileManager.h"
#include "Serialization/JsonSerializer.h"

AToyArena::AToyArena(){PrimaryActorTick.bCanEverTick=true;}
AStaticMeshActor* AToyArena::Shape(FVector P,FVector S,const TCHAR* Mesh,const TCHAR* Material,bool Collision)
{
 auto* A=GetWorld()->SpawnActor<AStaticMeshActor>(P,FRotator::ZeroRotator);
 auto* C=A->GetStaticMeshComponent(); C->SetMobility(EComponentMobility::Movable);
 C->SetStaticMesh(LoadObject<UStaticMesh>(nullptr,Mesh)); A->SetActorScale3D(S);
 if(auto* M=LoadObject<UMaterialInterface>(nullptr,Material)) C->SetMaterial(0,M);
 C->SetCollisionProfileName(Collision?TEXT("BlockAllDynamic"):TEXT("NoCollision"));
 C->SetCanEverAffectNavigation(false); return A;
}
void AToyArena::BeginPlay()
{
 Super::BeginPlay();
 auto* GM=GetWorld()->GetAuthGameMode<AToyGameMode>(); Toy=GM?GM->Toy:nullptr;
 if(!Toy)return;
 auto* PC=GetWorld()->GetFirstPlayerController();
 if(auto* Old=Toy->GetController()){Old->UnPossess();Old->Destroy();}
 PC->Possess(Toy); PC->bAutoManageActiveCameraTarget=false;
 Toy->EnableRiggedBlockout();
 Toy->PlaceholderLabel->SetHiddenInGame(true);
 Toy->GetCapsuleComponent()->SetCollisionResponseToChannel(ECC_Visibility,ECR_Block);
 auto* Move=Toy->GetCharacterMovement(); Move->MaxWalkSpeed=420; Move->MaxAcceleration=3600;
 Move->BrakingDecelerationWalking=3000; Move->JumpZVelocity=480; Move->AirControl=.55f;
 Move->GravityScale=1.6f;
 if(TActorIterator<ACameraActor> It{GetWorld()};It)Camera=*It;
 if(!Camera)Camera=GetWorld()->SpawnActor<ACameraActor>();
 Camera->GetCameraComponent()->SetConstraintAspectRatio(false); Camera->GetCameraComponent()->SetAspectRatio(1.6f); Camera->GetCameraComponent()->SetFieldOfView(50);
 PC->SetViewTarget(Camera);
 // Existing islands provide two routes and block both movement and enemy shots.
 // A conspicuous, exposed pickup gives the open southern lane a purpose.
 Pickup=Shape(FVector(450,-550,35),FVector(.5,.5,.5),TEXT("/Engine/BasicShapes/Sphere.Sphere"),TEXT("/Game/Toy/Materials/M_Gold.M_Gold"));
 bVerify=FParse::Param(FCommandLine::Get(),TEXT("ArenaVerify"));
 Restart();
 bShowcase=FParse::Param(FCommandLine::Get(),TEXT("ToyShowcase"));
 if(bShowcase)
 {
  if(!Toy->bRiggedBlockoutReady){UE_LOG(LogTemp,Error,TEXT("Showcase requires the 3D rig"));FPlatformMisc::RequestExit(false);return;}
  ShowcaseDirectory=FPaths::ProjectSavedDir()/TEXT("ShowcaseFrames");
  FParse::Value(FCommandLine::Get(),TEXT("ShowcaseOutput="),ShowcaseDirectory);
  IFileManager::Get().MakeDirectory(*ShowcaseDirectory,true);
  FApp::SetUseFixedTimeStep(true);FApp::SetFixedDeltaTime(1.0/30.0);
  Move->MaxWalkSpeed=180;Move->bOrientRotationToMovement=false;
  Toy->SetActorRotation(FRotator(0,-70,0));PC->bShowMouseCursor=false;
  Pickup->SetActorHiddenInGame(true);
  if(Drone){TArray<AActor*> Children;Drone->GetAttachedActors(Children);for(auto* C:Children)C->Destroy();Drone->Destroy();Drone=nullptr;}
  Camera->GetCameraComponent()->SetAspectRatio(9.f/16.f);Camera->GetCameraComponent()->SetFieldOfView(35);
 }
}
void AToyArena::Restart()
{
 Health=100;Remaining=60;Score=0;Swing=-1;Clock=0;ShootAt=2;RespawnAt=0;PickupAt=0;
 Toy->RigAction=0;
 DodgeUntil=DodgeReady=InvulnerableUntil=0;bTelegraph=false;HitFlash=Shake=0;
 for(auto& B:Bolts)if(B.Actor.IsValid())B.Actor->Destroy();Bolts.Empty();
 Toy->SetActorLocation(FVector(-350,-350,90));Toy->GetCharacterMovement()->StopMovementImmediately();Toy->SetIntent(EToyIntent::Idle);
 Pickup->SetActorHiddenInGame(false);SpawnDrone();
 Camera->SetActorLocation(Toy->GetActorLocation()+FVector(300,-600,700));
}
void AToyArena::SpawnDrone()
{
 if(Drone){TArray<AActor*> Children;Drone->GetAttachedActors(Children);for(auto* Child:Children)Child->Destroy();Drone->Destroy();}
 FVector Spawn(300,-100,125);
 const FVector Candidates[]={FVector(-650,-550,125),FVector(650,-550,125),FVector(-650,500,125)};
 for(const FVector& P:Candidates)if(FVector::Dist2D(P,Toy->GetActorLocation())>FVector::Dist2D(Spawn,Toy->GetActorLocation()))Spawn=P;
 Drone=Shape(Spawn,FVector(.95,.95,.55),TEXT("/Engine/BasicShapes/Sphere.Sphere"),TEXT("/Game/Toy/Materials/M_Purple.M_Purple"),true);
 DroneHealth=100;RespawnAt=0;ShootAt=Clock+2;bTelegraph=false;
 auto* Eye=Shape(Drone->GetActorLocation(),FVector(.28,.28,.28),TEXT("/Engine/BasicShapes/Sphere.Sphere"),TEXT("/Game/Toy/Materials/M_Gold.M_Gold"));
 Eye->AttachToActor(Drone,FAttachmentTransformRules::KeepWorldTransform);
 Eye->SetActorRelativeLocation(FVector(0,-45,0));
}
void AToyArena::Tone(float Frequency,float Duration,float Volume)
{
 auto* Wave=NewObject<USoundWaveProcedural>(this);Wave->SetSampleRate(22050);Wave->NumChannels=1;
 Wave->Duration=Duration;Wave->bLooping=false;
 TArray<int16> PCM;const int32 N=FMath::RoundToInt(22050*Duration);PCM.SetNumUninitialized(N);
 for(int32 I=0;I<N;++I){float T=float(I)/N;PCM[I]=int16(Volume*12000*FMath::Sin(2*PI*Frequency*I/22050.f)*(1-T)*FMath::Min(T*30,1.f));}
 Wave->QueueAudio(reinterpret_cast<const uint8*>(PCM.GetData()),N*sizeof(int16));
 if(auto* Audio=UGameplayStatics::SpawnSound2D(this,Wave))Audio->FadeOut(Duration,0);
}
void AToyArena::Attack()
{
 if(!IsPlaying() || Swing>=0)return;
 Swing=0;bHitThisSwing=false;Toy->StartRigAction(1);Toy->SetIntent(EToyIntent::SwordSwing);Tone(260,.10f,.35f);
}
void AToyArena::Dodge()
{
 if(!IsPlaying() || Clock<DodgeReady || Toy->GetCharacterMovement()->IsFalling())return;
 FVector Dir=MoveDirection.IsNearlyZero()?Aim:MoveDirection;
 Toy->LaunchCharacter(Dir.GetSafeNormal2D()*1050+FVector(0,0,65),true,true);
 Toy->StartRigAction(2);
 DodgeUntil=Clock+.22f;DodgeReady=Clock+1;InvulnerableUntil=Clock+.18f;++Dodges;Tone(150,.12f,.3f);
}
void AToyArena::DamagePlayer(float Amount)
{
 if(!IsPlaying() || Clock<InvulnerableUntil)return;
 Health=FMath::Max(0.f,Health-Amount);InvulnerableUntil=Clock+.55f;HitFlash=.22f;Shake=.18f;++DamageEvents;
 Tone(95,.18f,.6f);
 if(Health<=0)Toy->GetCharacterMovement()->StopMovementImmediately();
}
void AToyArena::Impact(FVector P,bool bEnemy)
{
 Shake=.14f;Tone(bEnemy?600:180,.12f,.55f);
 for(int I=0;I<7;++I){float A=I*2*PI/7;auto* Spark=Shape(P+FVector(FMath::Cos(A)*45,FMath::Sin(A)*45,20),FVector(.06,.06,.3),TEXT("/Engine/BasicShapes/Cube.Cube"),TEXT("/Game/Toy/Materials/M_Gold.M_Gold"));Spark->SetActorRotation(FRotator(I*25,I*51,0));Spark->SetLifeSpan(.16f);}
}
void AToyArena::UpdateDrone(float Dt)
{
 if(!Drone){if(Clock>=RespawnAt)SpawnDrone();return;}
 FVector P=Drone->GetActorLocation(),To=Toy->GetActorLocation()-P;To.Z=0;
 // Chase at long range, hold a readable firing distance, strafe up close.
 FVector Dir=To.GetSafeNormal();float Dist=To.Size();
 FVector Motion=Dist>480?Dir:Dist<240?-Dir:FVector(-Dir.Y,Dir.X,0)*.7f;
 if(!bTelegraph){FHitResult Hit;Drone->SetActorLocation(P+Motion*150*Dt,true,&Hit);if(Hit.bBlockingHit)Drone->AddActorWorldOffset(FVector(-Motion.Y,Motion.X,0)*150*Dt,true);}
 P=Drone->GetActorLocation();P.Z=125+FMath::Sin(Clock*3)*8;Drone->SetActorLocation(P);
 if(!bTelegraph && Clock>ShootAt-.7f){bTelegraph=true;LockedShot=(Toy->GetActorLocation()-P).GetSafeNormal();Tone(800,.10f,.2f);}
 if(bTelegraph)
 {
  DrawDebugLine(GetWorld(),P,P+LockedShot*900,FColor(255,100,40),false,-1,0,3);
  DrawDebugSphere(GetWorld(),P,65,16,FColor(255,80,40),false,-1,0,2);
 }
 if(Clock>=ShootAt)
 {
  FVector Origin=P+LockedShot*65;
  auto* Ball=Shape(Origin,FVector(.20),TEXT("/Engine/BasicShapes/Sphere.Sphere"),TEXT("/Game/Toy/Materials/M_Gold.M_Gold"));
  Bolts.Add({Ball,LockedShot*540,0});++Shots;ShootAt=Clock+2;bTelegraph=false;Tone(380,.10f,.3f);
 }
}
void AToyArena::UpdateBolts(float Dt)
{
 for(int I=Bolts.Num()-1;I>=0;--I)
 {
  auto& B=Bolts[I];if(!B.Actor.IsValid()){Bolts.RemoveAtSwap(I);continue;}
  FVector From=B.Actor->GetActorLocation(),To=From+B.Velocity*Dt;
  FHitResult Hit;FCollisionQueryParams Q;Q.AddIgnoredActor(B.Actor.Get());if(Drone)Q.AddIgnoredActor(Drone);
  bool Blocked=GetWorld()->SweepSingleByChannel(Hit,From,To,FQuat::Identity,ECC_Visibility,FCollisionShape::MakeSphere(10),Q);
  B.Life+=Dt;
  if(Blocked || B.Life>4)
  {
   if(Hit.GetActor()==Toy)DamagePlayer(20);
   if(Blocked)Impact(Hit.ImpactPoint,false);
   B.Actor->Destroy();Bolts.RemoveAtSwap(I);
  }
  else B.Actor->SetActorLocation(To);
 }
}
void AToyArena::Tick(float Dt)
{
 Super::Tick(Dt);if(!Toy)return;
#if WITH_EDITOR
 if((bVerify || bShowcase) && GShaderCompilingManager && GShaderCompilingManager->IsCompiling())return;
#endif
 if(bShowcase){TickShowcase(Dt);return;}
 Clock+=Dt;HitFlash=FMath::Max(0.f,HitFlash-Dt);Shake=FMath::Max(0.f,Shake-Dt);
 auto* PC=GetWorld()->GetFirstPlayerController();
 if(IsPlaying())
 {
  Remaining=FMath::Max(0.f,Remaining-Dt);
  FVector Ray,Direction;
  if(!bVerify && PC->DeprojectMousePositionToWorld(Ray,Direction) && FMath::Abs(Direction.Z)>.001)
  {float T=(Toy->GetActorLocation().Z-Ray.Z)/Direction.Z;if(T>0)Aim=(Ray+Direction*T-Toy->GetActorLocation()).GetSafeNormal2D();}
  if(!MoveDirection.IsNearlyZero() && Clock>=DodgeUntil)Toy->AddMovementInput(MoveDirection,1);
  if(Clock<DodgeUntil)DrawDebugCircle(GetWorld(),Toy->GetActorLocation()-FVector(0,0,80),48,24,FColor::Cyan,false,-1,0,3,FVector(1,0,0),FVector(0,1,0),false);
  if(Toy->bRiggedBlockoutReady)
  {
   Toy->GetCharacterMovement()->bOrientRotationToMovement=false;
   FVector Facing=(Swing>=0 || MoveDirection.IsNearlyZero())?Aim:MoveDirection;
   Toy->SetActorRotation(FMath::RInterpTo(Toy->GetActorRotation(),Facing.Rotation(),Dt,Swing>=0?24.f:14.f));
  }
  UpdateDrone(Dt);UpdateBolts(Dt);
  if(Swing>=0)
  {
   const float PreviousSwing=Swing;Swing+=Dt;
   if(Swing>=.12f && PreviousSwing<=.30f)
   {
    const FVector P=Toy->GetActorLocation();
    const float Angle=FMath::Lerp(-65.f,65.f,FMath::Clamp((Swing-.12f)/.18f,0.f,1.f));
    FVector Tip=P+Aim.RotateAngleAxis(Angle,FVector::UpVector)*185;
    DrawDebugLine(GetWorld(),P+Aim*40,Tip,FColor::Cyan,false,.07f,0,9);
    if(Drone && !bHitThisSwing)
    {
     FVector To=Drone->GetActorLocation()-P;
     FHitResult Obstacle;FCollisionQueryParams Q;Q.AddIgnoredActor(Toy);
     bool Hit=GetWorld()->LineTraceSingleByChannel(Obstacle,P,Drone->GetActorLocation(),ECC_Visibility,Q);
     if(To.Size()<220 && FVector::DotProduct(To.GetSafeNormal2D(),Aim)>.35f && (!Hit || Obstacle.GetActor()==Drone))
     {
      bHitThisSwing=true;DroneHealth-=40;++Hits;Impact(Drone->GetActorLocation(),true);
      Drone->AddActorWorldOffset(To.GetSafeNormal2D()*55,true);
      if(DroneHealth<=0)
      {
       TArray<AActor*> Children;Drone->GetAttachedActors(Children);for(auto* Child:Children)Child->Destroy();
       Drone->Destroy();Drone=nullptr;Score+=100;RespawnAt=Clock+2.5f;
      }
     }
    }
   }
   if(Swing>=.55f){Swing=-1;Toy->SetIntent(EToyIntent::Idle);}
  }
  if(Clock>=PickupAt)
  {
   Pickup->SetActorHiddenInGame(false);Pickup->AddActorLocalRotation(FRotator(0,90*Dt,0));
   if(Health<100 && FVector::Dist2D(Toy->GetActorLocation(),Pickup->GetActorLocation())<65)
   {Health=FMath::Min(100.f,Health+35);PickupAt=Clock+8;Pickup->SetActorHiddenInGame(true);++Collected;Tone(1000,.2f,.35f);}
  }
 }
 else {MoveDirection=FVector::ZeroVector;Toy->SetIntent(EToyIntent::Idle);}
 FVector Focus=Toy->GetActorLocation();
 if(Drone)Focus=FMath::Lerp(Focus,Drone->GetActorLocation(),.35f);
 const float Framing=Drone?FMath::Clamp(float(FVector::Dist2D(Toy->GetActorLocation(),Drone->GetActorLocation()))/650.f,1.f,2.4f):1.f;
 FVector Goal=Focus+FVector(300,-600,700)*Framing;
 Camera->SetActorLocation(FMath::VInterpTo(Camera->GetActorLocation(),Goal,Dt,5));
 Camera->SetActorRotation((Focus-Camera->GetActorLocation()).Rotation()+FRotator(Shake*FMath::Sin(Clock*90),0,0));
 if(bVerify)Verify(Dt);
}
void AToyArena::Draw(AToyHUD* H,UCanvas* C)
{
 if(bShowcase)return;
 float W=C->ClipX;
 H->DrawRect(FLinearColor(.02,.025,.04,.8),18,18,250,66);
 H->DrawText(FString::Printf(TEXT("HEALTH %03d    SCORE %03d"),int(Health),Score),FLinearColor::White,30,26,nullptr,1.2);
 H->DrawRect(FLinearColor(.15,.18,.22,1),30,55,220,8);
 H->DrawRect(FLinearColor(.1,.85,.7,1),30,55,220*Health/100,8);
 H->DrawText(FString::Printf(TEXT("%02d SEC"),FMath::CeilToInt(Remaining)),FLinearColor::White,W-110,25,nullptr,1.4);
 H->DrawText(Clock>=DodgeReady?TEXT("DODGE READY"):TEXT("DODGE RECHARGING"),FLinearColor(.25,.9,1),30,92);
 H->DrawRect(FLinearColor(.02,.025,.04,.75),18,C->ClipY-42,FMath::Min(W-36,750.f),30);
 H->DrawText(TEXT("WASD move   Mouse aim   Click / 8 slash   Shift dodge   Space jump   R restart"),FLinearColor::White,24,C->ClipY-34,nullptr,.95);
 if(Drone)
 {
  FVector P=H->Project(Drone->GetActorLocation()+FVector(0,0,65));
  H->DrawRect(FLinearColor(.05,.05,.08,1),P.X-35,P.Y,70,6);
  H->DrawRect(FLinearColor(1,.3,.3,1),P.X-35,P.Y,70*DroneHealth/100,6);
 }
 float X,Y;if(H->GetOwningPlayerController()->GetMousePosition(X,Y)){H->DrawLine(X-7,Y,X+7,Y,FLinearColor::White);H->DrawLine(X,Y-7,X,Y+7,FLinearColor::White);}
 if(HitFlash>0)H->DrawRect(FLinearColor(1,0,.03,HitFlash*.6),0,0,W,C->ClipY);
 if(!IsPlaying())
 {
  H->DrawRect(FLinearColor(0,0,0,.7),W*.2,C->ClipY*.4,W*.6,100);
  H->DrawText(Health<=0?TEXT("KNOCKED OUT"):TEXT("ROUND COMPLETE"),FLinearColor::White,W*.25,C->ClipY*.42,nullptr,1.6);
  H->DrawText(FString::Printf(TEXT("Score %d  |  R to play again"),Score),FLinearColor::White,W*.25,C->ClipY*.42+38);
 }
}
// Bounded integration scenario: the actual movement, attack, projectile and pickup
// paths run in Unreal. This does not claim to test physical keyboard focus.
void AToyArena::Verify(float Dt)
{
 auto* PC=Cast<AToyPlayerController>(GetWorld()->GetFirstPlayerController());
 TestAge+=Dt;
 if(Toy->bRiggedBlockoutReady)
 {
  auto* M=Toy->GetMesh();
  FVector Foot=M->GetBoneTransform(M->GetBoneIndex(TEXT("foot_l")),FTransform::Identity).GetLocation();
  FVector Hand=M->GetBoneTransform(M->GetBoneIndex(TEXT("hand_r")),FTransform::Identity).GetLocation();
  FVector Head=M->GetBoneTransform(M->GetBoneIndex(TEXT("head")),FTransform::Identity).GetLocation();
  if(TestAge>Dt*2)
  {
   if(VerifyStage==1)RigRunMotion=FMath::Max(RigRunMotion,float(FVector::Dist(Foot,RigPreviousFoot)));

   if(VerifyStage==3)RigSlashMotion=FMath::Max(RigSlashMotion,float(FVector::Dist(Hand,RigPreviousHand)));
  }
  if(VerifyStage==0)RigPreviousHead=Head;
  if(VerifyStage==2)RigDodgeMotion=FMath::Max(RigDodgeMotion,float(FVector::Dist(Head,RigPreviousHead)));
  RigPreviousFoot=Foot;RigPreviousHand=Hand;
  int32 Bit=VerifyStage<=3?(1<<VerifyStage):0;
  float CaptureAt=VerifyStage==0?.8f:VerifyStage==1?.3f:.16f;
  if(Bit && !(RigCaptureMask&Bit) && TestAge>CaptureAt)
  {
   FScreenshotRequest::RequestScreenshot(FPaths::ProjectSavedDir()/FString::Printf(TEXT("Verification/rig-%d.png"),VerifyStage),true,false);RigCaptureMask|=Bit;
  }
 }

 auto Next=[this](){++VerifyStage;TestAge=0;};
 switch(VerifyStage)
 {
 case 0: if(TestAge>1){TestStart=Toy->GetActorLocation();MoveDirection=FVector(1,0,0);ShootAt=100;Next();} break;
 case 1: if(TestAge>1){Checks.Add(TEXT("direct_movement"),Toy->GetActorLocation().X-TestStart.X>150);UE_LOG(LogTemp,Display,TEXT("ARENA movement %s -> %s"),*TestStart.ToString(),*Toy->GetActorLocation().ToString());TestStart=Toy->GetActorLocation();MoveDirection=FVector(0,-1,0);PC->CombatDodge();PC->CombatDodge();Checks.Add(TEXT("dodge_cooldown"),Dodges==1);Next();} break;
 case 2: if(TestAge>.5f){MoveDirection=FVector::ZeroVector;Checks.Add(TEXT("dodge_displacement"),Toy->GetActorLocation().Y<TestStart.Y-100);Toy->SetActorLocation(FVector(-600,-500,90));Toy->GetCharacterMovement()->StopMovementImmediately();Aim=FVector(1,0,0);Drone->SetActorLocation(FVector(-450,-500,125));PC->CombatAttack();PC->CombatAttack();Next();} break;
 case 3: if(TestAge>.7f){Checks.Add(TEXT("sword_once_per_swing"),Hits==1 && DroneHealth==60);Drone->SetActorLocation(Toy->GetActorLocation()+FVector(150,0,35));PC->CombatAttack();Next();} break;
 case 4: if(TestAge>.7f){Drone->SetActorLocation(Toy->GetActorLocation()+FVector(150,0,35));PC->CombatAttack();Next();} break;
 case 5: if(TestAge>.7f){Checks.Add(TEXT("kill_scores"),Score==100 && !Drone);Next();} break;
 case 6: if(TestAge>3){Checks.Add(TEXT("drone_respawns"),Drone!=nullptr);Toy->SetActorLocation(FVector(-600,-500,90));Toy->GetCharacterMovement()->StopMovementImmediately();Drone->SetActorLocation(FVector(-100,-500,100));MoveDirection=FVector::ZeroVector;ShootAt=Clock+.8f;Next();} break;
 case 7: if(TestAge>3){Checks.Add(TEXT("projectile_damages"),Health<100 && Shots>0 && DamageEvents>0);Health=50;Toy->SetActorLocation(Pickup->GetActorLocation()+FVector(0,0,55));ShootAt=Clock+100;Next();} break;
 case 8: if(TestAge>.2f){Checks.Add(TEXT("pickup_heals"),Health==85 && Collected==1 && Pickup->IsHidden());Toy->SetActorLocation(FVector(-600,-500,90));Toy->GetCharacterMovement()->StopMovementImmediately();PC->CombatJump();TestStart=Toy->GetActorLocation();Next();} break;
 case 9: if(TestAge>.2f){Checks.Add(TEXT("jump_rises"),Toy->GetActorLocation().Z>TestStart.Z+20);Next();} break;
 case 10: if(TestAge>1){Checks.Add(TEXT("jump_lands"),!Toy->GetCharacterMovement()->IsFalling());Toy->SetActorLocation(FVector(170,-100,90));MoveDirection=FVector(0,1,0);Next();} break;
 case 11: if(TestAge>.7f){Checks.Add(TEXT("island_blocks_capsule"),Toy->GetActorLocation().Y<-8);MoveDirection=FVector::ZeroVector;Toy->GetCharacterMovement()->StopMovementImmediately();Toy->SetActorLocation(FVector(-350,-350,90));Drone->SetActorLocation(FVector(0,-250,125));Next();} break;
 case 12: if(TestAge>1){FScreenshotRequest::RequestScreenshot(FPaths::ProjectSavedDir()/TEXT("Verification/arena.png"),true,false);Next();} break;
 case 13: if(TestAge>.3f){Remaining=.01f;Next();} break;
 case 14: if(TestAge>.1f){Checks.Add(TEXT("round_ends"),!IsPlaying());PC->CombatRestart();Checks.Add(TEXT("restart_resets"),Health==100 && Score==0 && Remaining==60 && Drone!=nullptr);InvulnerableUntil=0;DamagePlayer(100);Checks.Add(TEXT("death_ends_round"),!IsPlaying());FinishVerify();Next();} break;
 }
}
void AToyArena::FinishVerify()
{
 if(!FParse::Param(FCommandLine::Get(),TEXT("Toy2D")))
 {
  Checks.Add(TEXT("rig_active"),Toy->bRiggedBlockoutReady);
  Checks.Add(TEXT("rig_run_changes_feet"),RigRunMotion>.1f);
  Checks.Add(TEXT("rig_slash_changes_hand"),RigSlashMotion>.1f);
  Checks.Add(TEXT("rig_dodge_changes_head"),RigDodgeMotion>.1f);
  Checks.Add(TEXT("rig_capsule_authority"),!Toy->GetMesh()->IsSimulatingPhysics() && Toy->GetMesh()->GetCollisionEnabled()==ECollisionEnabled::NoCollision);
 }
 auto R=MakeShared<FJsonObject>();bool Pass=Checks.Num()>=14;
 R->SetNumberField(TEXT("run_foot_frame_motion_cm"),RigRunMotion);R->SetNumberField(TEXT("slash_hand_frame_motion_cm"),RigSlashMotion);R->SetNumberField(TEXT("dodge_head_frame_motion_cm"),RigDodgeMotion);
 for(const auto& C:Checks){R->SetBoolField(C.Key,C.Value);Pass&=C.Value;}
 R->SetBoolField(TEXT("passed"),Pass);R->SetStringField(TEXT("scope"),TEXT("Unreal runtime integration; controller action handlers, not OS input. Rigged blockout motion and combat; visual captures reviewed separately."));
 FString Json;auto Writer=TJsonWriterFactory<>::Create(&Json);FJsonSerializer::Serialize(R,Writer);
 FFileHelper::SaveStringToFile(Json,*(FPaths::ProjectSavedDir()/TEXT("Verification/arena.json")));
 UE_LOG(LogTemp,Display,TEXT("ARENA VERIFY %s %s"),Pass?TEXT("PASS"):TEXT("FAIL"),*Json);
 FPlatformMisc::RequestExitWithStatus(false,Pass?0:1);
}
