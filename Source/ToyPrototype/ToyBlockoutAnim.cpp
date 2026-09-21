#include "ToyBlockoutAnim.h"
#include "ToyCharacter.h"
#include "Engine/World.h"
#include "Animation/AnimInstanceProxy.h"
#include "Animation/AnimSequence.h"
#include "Animation/AnimNode_SequencePlayer.h"
#include "AnimNodes/AnimNode_SequenceEvaluator.h"
#include "AnimNodes/AnimNode_TwoWayBlend.h"
#include "UObject/ConstructorHelpers.h"
struct FBlockoutProxy : FAnimInstanceProxy
{
 FAnimNode_SequencePlayer_Standalone IdlePlayer,RunPlayer;
 FAnimNode_SequenceEvaluator_Standalone Action;
 FAnimNode_TwoWayBlend Locomotion,Final;
 explicit FBlockoutProxy(UAnimInstance* I):FAnimInstanceProxy(I)
 {Locomotion.A.SetLinkNode(&IdlePlayer);Locomotion.B.SetLinkNode(&RunPlayer);Final.A.SetLinkNode(&Locomotion);Final.B.SetLinkNode(&Action);}
 virtual FAnimNode_Base* GetCustomRootNode() override{return &Final;}
 virtual void Initialize(UAnimInstance* I) override
 {
  auto* A=CastChecked<UToyBlockoutAnim>(I);IdlePlayer.SetSequence(A->Idle);RunPlayer.SetSequence(A->Run);
  IdlePlayer.SetLoopAnimation(true);RunPlayer.SetLoopAnimation(true);Action.SetSequence(A->Slash);
  FAnimInstanceProxy::Initialize(I);
 }
 virtual void PreUpdate(UAnimInstance* I,float Dt) override
 {
  FAnimInstanceProxy::PreUpdate(I,Dt);
  auto* T=Cast<AToyCharacter>(I->TryGetPawnOwner());auto* A=CastChecked<UToyBlockoutAnim>(I);if(!T)return;
  float Speed=T->GetVelocity().Size2D();
  Locomotion.Alpha=FMath::FInterpTo(Locomotion.Alpha,FMath::Clamp(Speed/120.f,0.f,1.f),Dt,12);
  RunPlayer.SetPlayRate(FMath::Clamp(Speed/230.f,.4f,2.2f));
  float Age=T->GetWorld()->GetTimeSeconds()-T->RigActionStarted;
  float Duration=T->RigAction==2?.4f:.55f;
  if(T->RigAction && Age<Duration)
  {
   UAnimSequence* Clip=T->RigAction==2?A->Dodge.Get():A->Slash.Get();
   Action.SetSequence(Clip);Action.SetExplicitTime(Clip?FMath::Clamp(Age/Duration,0.f,1.f)*Clip->GetPlayLength():0);
   Final.Alpha=FMath::Min(FMath::Clamp(Age/.04f,0.f,1.f),FMath::Clamp((Duration-Age)/.09f,0.f,1.f));
  }
  else Final.Alpha=FMath::FInterpTo(Final.Alpha,0.f,Dt,20);
 }
 virtual bool Evaluate(FPoseContext& O) override{Final.Evaluate_AnyThread(O);return true;}
};
UToyBlockoutAnim::UToyBlockoutAnim()
{
 static ConstructorHelpers::FObjectFinder<UAnimSequence> I(TEXT("/Game/Toy/Blockout/A_ToyIdle.A_ToyIdle"));Idle=I.Object;
 static ConstructorHelpers::FObjectFinder<UAnimSequence> R(TEXT("/Game/Toy/Blockout/A_ToyRun.A_ToyRun"));Run=R.Object;
 static ConstructorHelpers::FObjectFinder<UAnimSequence> D(TEXT("/Game/Toy/Blockout/A_ToyDodge.A_ToyDodge"));Dodge=D.Object;
 static ConstructorHelpers::FObjectFinder<UAnimSequence> S(TEXT("/Game/Toy/Blockout/A_ToySlash.A_ToySlash"));Slash=S.Object;
 bUseMultiThreadedAnimationUpdate=false;
}
FAnimInstanceProxy* UToyBlockoutAnim::CreateAnimInstanceProxy(){return new FBlockoutProxy(this);}
void UToyBlockoutAnim::DestroyAnimInstanceProxy(FAnimInstanceProxy* P){delete P;}
