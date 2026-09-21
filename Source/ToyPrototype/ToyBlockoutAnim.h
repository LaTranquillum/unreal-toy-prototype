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
 virtual FAnimInstanceProxy* CreateAnimInstanceProxy() override;
 virtual void DestroyAnimInstanceProxy(FAnimInstanceProxy* Proxy) override;
};
