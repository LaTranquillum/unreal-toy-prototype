#include "ToyAnimInstance.h"
#include "ToyCharacter.h"
#include "Animation/AnimInstanceProxy.h"
#include "Animation/AnimSequence.h"
#include "Animation/AnimNode_SequencePlayer.h"
#include "AnimNodes/AnimNode_TwoWayBlend.h"
#include "UObject/ConstructorHelpers.h"

struct FToyAnimProxy : FAnimInstanceProxy
{
    FAnimNode_SequencePlayer_Standalone Idle, Walk;
    FAnimNode_TwoWayBlend Blend;
    float LookAlpha=0, GestureAlpha=0, Time=0;
    explicit FToyAnimProxy(UAnimInstance* Instance) : FAnimInstanceProxy(Instance)
    {
        Blend.A.SetLinkNode(&Idle); Blend.B.SetLinkNode(&Walk);
    }
    virtual FAnimNode_Base* GetCustomRootNode() override { return &Blend; }
    virtual void Initialize(UAnimInstance* Instance) override
    {
        UToyAnimInstance* Anim = CastChecked<UToyAnimInstance>(Instance);
        Idle.SetSequence(Anim->IdleSequence); Walk.SetSequence(Anim->WalkSequence);
        Idle.SetLoopAnimation(true); Walk.SetLoopAnimation(true);
        FAnimInstanceProxy::Initialize(Instance);
    }
    virtual void PreUpdate(UAnimInstance* Instance, float Delta) override
    {
        FAnimInstanceProxy::PreUpdate(Instance, Delta);
        if (const AToyCharacter* Toy = Cast<AToyCharacter>(Instance->TryGetPawnOwner()))
        {
            const float Speed = Toy->GetVelocity().Size2D();
            Blend.Alpha=FMath::FInterpTo(Blend.Alpha, FMath::Clamp(Speed/90.f,0.f,1.f),Delta,8.f);
            Walk.SetPlayRate(FMath::Clamp(Speed/150.f,.35f,1.6f));
            LookAlpha=FMath::FInterpTo(LookAlpha,Toy->Intent==EToyIntent::LookAround?1.f:0.f,Delta,5.f);
            GestureAlpha=FMath::FInterpTo(GestureAlpha,Toy->Intent==EToyIntent::Gesture?1.f:0.f,Delta,5.f);
            Time+=Delta;
        }
    }
    virtual bool Evaluate(FPoseContext& Output) override
    {
        Blend.Evaluate_AnyThread(Output);
        // Small authored pose offsets on top of real animation; evaluated before physical animation.
        auto Rotate=[&](FName Bone, FRotator Rotation)
        {
            const FBoneContainer& Bones=Output.Pose.GetBoneContainer();
            const int32 MeshIndex=Bones.GetPoseBoneIndexForBoneName(Bone);
            if (MeshIndex==INDEX_NONE) return;
            const FCompactPoseBoneIndex Index=Bones.MakeCompactPoseIndex(FMeshPoseBoneIndex(MeshIndex));
            if (Index.GetInt()==INDEX_NONE) return;
            FTransform& Transform=Output.Pose[Index];
            Transform.SetRotation((Transform.GetRotation()*Rotation.Quaternion()).GetNormalized());
        };
        Rotate(TEXT("head"),FRotator(0,0,22.f*FMath::Sin(Time*1.6f)*LookAlpha));
        Rotate(TEXT("upperarm_r"),FRotator(-40.f*GestureAlpha,0,0));
        Rotate(TEXT("lowerarm_r"),FRotator(-25.f*GestureAlpha,0,0));
        Rotate(TEXT("hand_r"),FRotator(12.f*FMath::Sin(Time*5.f)*GestureAlpha,0,0));
        return true;
    }
};

UToyAnimInstance::UToyAnimInstance()
{
    static ConstructorHelpers::FObjectFinder<UAnimSequence> Idle(TEXT("/Game/Mannequin/Animations/ThirdPersonIdle.ThirdPersonIdle"));
    static ConstructorHelpers::FObjectFinder<UAnimSequence> Walk(TEXT("/Game/Mannequin/Animations/ThirdPersonWalk.ThirdPersonWalk"));
    IdleSequence=Idle.Object; WalkSequence=Walk.Object;
    bUseMultiThreadedAnimationUpdate=false;
}
FAnimInstanceProxy* UToyAnimInstance::CreateAnimInstanceProxy() { return new FToyAnimProxy(this); }
void UToyAnimInstance::DestroyAnimInstanceProxy(FAnimInstanceProxy* Proxy) { delete Proxy; }
