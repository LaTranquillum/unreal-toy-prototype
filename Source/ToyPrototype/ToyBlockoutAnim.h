#pragma once
#include "CoreMinimal.h"
#include "Animation/AnimInstance.h"
#include "ToyBlockoutAnim.generated.h"
UCLASS(Transient)
class TOYPROTOTYPE_API UToyBlockoutAnim : public UAnimInstance
{
 GENERATED_BODY()
public:
 UToyBlockoutAnim();
 UPROPERTY() TObjectPtr<class UAnimSequence> Idle;
 UPROPERTY() TObjectPtr<class UAnimSequence> Run;
 UPROPERTY() TObjectPtr<class UAnimSequence> Dodge;
 UPROPERTY() TObjectPtr<class UAnimSequence> Slash;
 virtual void NativeUpdateAnimation(float DeltaSeconds) override;
 float FocusedWeight=0.f;
 float ShoutWeight=0.f;
 float BlinkWeight=0.f;
 float BlinkClock=0.f;
 virtual FAnimInstanceProxy* CreateAnimInstanceProxy() override;
 virtual void DestroyAnimInstanceProxy(FAnimInstanceProxy* Proxy) override;
};
