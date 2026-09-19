#pragma once
#include "CoreMinimal.h"
#include "Animation/AnimInstance.h"
#include "ToyAnimInstance.generated.h"
UCLASS(Transient)
class TOYPROTOTYPE_API UToyAnimInstance : public UAnimInstance
{
    GENERATED_BODY()
public:
    UToyAnimInstance();
    UPROPERTY() TObjectPtr<class UAnimSequence> IdleSequence;
    UPROPERTY() TObjectPtr<class UAnimSequence> WalkSequence;
    virtual FAnimInstanceProxy* CreateAnimInstanceProxy() override;
    virtual void DestroyAnimInstanceProxy(FAnimInstanceProxy* Proxy) override;
};
