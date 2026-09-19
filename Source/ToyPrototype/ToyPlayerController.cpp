#include "ToyPlayerController.h"
#include "ToyGameMode.h"
#include "ToyCharacter.h"
#include "ToyAIController.h"
#include "Components/InputComponent.h"
#include "Engine/World.h"
#include "InputKeyEventArgs.h"
#include "TimerManager.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "Misc/Paths.h"
#include "Misc/FileHelper.h"
#include "Serialization/JsonSerializer.h"
void AToyPlayerController::BeginPlay()
{
 Super::BeginPlay();
 bShowMouseCursor=true; bEnableClickEvents=true;
 FInputModeGameOnly Mode; Mode.SetConsumeCaptureMouseDown(false); SetInputMode(Mode);
 if (FParse::Param(FCommandLine::Get(),TEXT("ToyControlVerify")))
 {
  FTimerHandle Handle;
  TSharedRef<FJsonObject> Results=MakeShared<FJsonObject>();
  GetWorldTimerManager().SetTimer(Handle,[this,Age=0.f,Stage=0,Passed=true,Start=FVector::ZeroVector,BeforeLook=0,Results]() mutable
  {
   Age+=.1f;
   AToyGameMode* GM=GetWorld()->GetAuthGameMode<AToyGameMode>();
   if (!GM || !GM->Toy) return;
   AToyCharacter* T=GM->Toy;
   AToyAIController* AI=Cast<AToyAIController>(T->GetController());
   if (!AI) return;
   auto Press=[this](FKey Key)
   {
    InputKey(FInputKeyEventArgs::CreateSimulated(Key,IE_Pressed,1));
    FTimerHandle Release;
    GetWorldTimerManager().SetTimer(Release,[this,Key](){InputKey(FInputKeyEventArgs::CreateSimulated(Key,IE_Released,0));},.05f,false);
   };
   auto Check=[&](const TCHAR* Name,bool Value){Results->SetBoolField(Name,Value);Passed&=Value;};
   if(Age>1 && Stage==0){Press(EKeys::One);Stage=1;}
   if(Age>5 && Stage==1){Check(TEXT("key_1_stop_holds"),CommandsReceived[1]>0 && AI->bManualControl && T->Intent==EToyIntent::Idle && T->GetVelocity().Size2D()<1);Start=T->GetActorLocation();Press(EKeys::Two);Stage=2;}
   if(Age>9 && Stage==2){Check(TEXT("key_2_wander_moves"),CommandsReceived[2]>0 && AI->bManualControl && AI->ManualIntent==EToyIntent::Wander && FVector::Dist2D(Start,T->GetActorLocation())>80);BeforeLook=T->LookTurnCount;Press(EKeys::Three);Stage=3;}
   if(Age>13 && Stage==3){Check(TEXT("key_3_look_visible"),CommandsReceived[3]>0 && T->Intent==EToyIntent::LookAround && T->LookTurnCount-BeforeLook>=2 && T->GetVelocity().Size2D()<1);Press(EKeys::Four);Stage=4;}
   if(Age>17 && Stage==4){Check(TEXT("key_4_sway_visible"),CommandsReceived[4]>0 && T->Intent==EToyIntent::Gesture && T->MaxCutoutLean>6 && T->GetVelocity().Size2D()<1);Press(EKeys::Five);Stage=5;}
   if(Age>19 && Stage==5){Check(TEXT("key_5_jump_and_land"),CommandsReceived[5]>0 && T->MaxJumpRise>20 && !T->GetCharacterMovement()->IsFalling());Press(EKeys::Six);Stage=6;}
   if(Age>21 && Stage==6){Check(TEXT("key_6_bend_pose"),CommandsReceived[6]>0 && T->bActionArtReady && T->CurrentActionFrame==3);Start=T->GetActorLocation();Press(EKeys::Seven);Stage=7;}
   if(Age>25 && Stage==7){Check(TEXT("key_7_crawl_moves"),CommandsReceived[7]>0 && FVector::Dist2D(Start,T->GetActorLocation())>40 && (T->CurrentActionFrame==1 || T->CurrentActionFrame==4));Press(EKeys::Eight);Stage=8;}
   if(Age>27 && Stage==8){Check(TEXT("key_8_sword_frames"),CommandsReceived[8]>0 && T->SwordFrameMask==3 && T->GetVelocity().Size2D()<1);if(AToyHUD* H=Cast<AToyHUD>(GetHUD()))H->NotifyHitBoxClick(TEXT("0"));Stage=9;}
   if(Age>28 && Stage==9)
   {
    Check(TEXT("hud_auto_handler"),CommandsReceived[0]>0 && !AI->bManualControl);
    Results->SetBoolField(TEXT("controls_pass"),Passed);
    Results->SetStringField(TEXT("method"),TEXT("Injected key events through PlayerController InputKey; HUD Auto callback dispatch. OS keyboard focus and physical mouse clicks not simulated."));
    FString Json;auto Writer=TJsonWriterFactory<>::Create(&Json);FJsonSerializer::Serialize(Results,Writer);
    FFileHelper::SaveStringToFile(Json,*(FPaths::ProjectSavedDir()/TEXT("Verification/controls.json")));
    UE_LOG(LogTemp,Display,TEXT("TOY CONTROLS %s %s"),Passed?TEXT("PASS"):TEXT("FAIL"),*Json);
    Stage=10;FPlatformMisc::RequestExitWithStatus(false,Passed?0:1);
   }
  },.1f,true);
 }
}
void AToyPlayerController::SetupInputComponent()
{
 Super::SetupInputComponent();
 for (FKey Key:{EKeys::One,EKeys::NumPadOne}) InputComponent->BindKey(Key,IE_Pressed,this,&AToyPlayerController::Idle);
 for (FKey Key:{EKeys::Two,EKeys::NumPadTwo}) InputComponent->BindKey(Key,IE_Pressed,this,&AToyPlayerController::Wander);
 for (FKey Key:{EKeys::Three,EKeys::NumPadThree}) InputComponent->BindKey(Key,IE_Pressed,this,&AToyPlayerController::Look);
 for (FKey Key:{EKeys::Four,EKeys::NumPadFour}) InputComponent->BindKey(Key,IE_Pressed,this,&AToyPlayerController::Sway);
 for (FKey Key:{EKeys::Five,EKeys::NumPadFive}) InputComponent->BindKey(Key,IE_Pressed,this,&AToyPlayerController::Hop);
 for (FKey Key:{EKeys::Six,EKeys::NumPadSix}) InputComponent->BindKey(Key,IE_Pressed,this,&AToyPlayerController::Bend);
 for (FKey Key:{EKeys::Seven,EKeys::NumPadSeven}) InputComponent->BindKey(Key,IE_Pressed,this,&AToyPlayerController::Crawl);
 for (FKey Key:{EKeys::Eight,EKeys::NumPadEight}) InputComponent->BindKey(Key,IE_Pressed,this,&AToyPlayerController::Sword);
 for (FKey Key:{EKeys::Zero,EKeys::NumPadZero,EKeys::A}) InputComponent->BindKey(Key,IE_Pressed,this,&AToyPlayerController::Auto);
 InputComponent->BindKey(EKeys::F,IE_Pressed,this,&AToyPlayerController::FailedPath);
 InputComponent->BindKey(EKeys::P,IE_Pressed,this,&AToyPlayerController::Impulse);
}
void AToyPlayerController::ToyAction(int32 Action)
{
 AToyGameMode* Mode=GetWorld()->GetAuthGameMode<AToyGameMode>();
 if (!Mode || !Mode->Toy || Action<0 || Action>8) return;
 if (AToyAIController* AI=Cast<AToyAIController>(Mode->Toy->GetController()))
 {
  ++CommandsReceived[Action];
  if (Action==0) AI->ResumeAutonomy();
  else AI->SetManualIntent(static_cast<EToyIntent>(Action-1));
  UE_LOG(LogTemp,Display,TEXT("TOY INPUT action=%d manual=%d"),Action,AI->bManualControl);
 }
}
void AToyPlayerController::Idle(){ToyAction(1);}
void AToyPlayerController::Wander(){ToyAction(2);}
void AToyPlayerController::Look(){ToyAction(3);}
void AToyPlayerController::Sway(){ToyAction(4);}
void AToyPlayerController::Auto(){ToyAction(0);}
void AToyPlayerController::FailedPath(){if (AToyGameMode* M=GetWorld()->GetAuthGameMode<AToyGameMode>()) if(M->Toy) if(AToyAIController* AI=Cast<AToyAIController>(M->Toy->GetController())) AI->TestUnreachableDestination();}
void AToyPlayerController::Impulse(){if (AToyGameMode* M=GetWorld()->GetAuthGameMode<AToyGameMode>()) if(M->Toy) M->Toy->PerturbOnce();}

void AToyPlayerController::Hop(){ToyAction(5);}
void AToyPlayerController::Bend(){ToyAction(6);}
void AToyPlayerController::Crawl(){ToyAction(7);}
void AToyPlayerController::Sword(){ToyAction(8);}
