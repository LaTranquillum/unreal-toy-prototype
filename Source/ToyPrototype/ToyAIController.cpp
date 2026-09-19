#include "ToyAIController.h"
#include "Engine/World.h"
#include "NavigationSystem.h"
#include "NavigationPath.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "TimerManager.h"

void AToyAIController::OnPossess(APawn* Pawn)
{
    Super::OnPossess(Pawn);
    Toy = Cast<AToyCharacter>(Pawn);
    if (!Toy) return;
    IntentRandom.Initialize(Toy->BehaviorSeed);
    NavigationRandom.Initialize(Toy->BehaviorSeed ^ 0x31a9);
    HomeLocation = Toy->GetActorLocation();
    NextDecisionTime = GetWorld()->GetTimeSeconds() + 1.5f;
    GetWorldTimerManager().SetTimer(ThinkTimer, this, &AToyAIController::Think, 0.25f, true);
}

void AToyAIController::OnUnPossess()
{
    GetWorldTimerManager().ClearTimer(ThinkTimer);
    Toy = nullptr;
    Super::OnUnPossess();
}

void AToyAIController::Think()
{
    if (!Toy) return;
    const float Now = GetWorld()->GetTimeSeconds();
    if (NavigationState != EToyNavigationState::Moving)
    {
        if (Now >= NextDecisionTime)
        {
            if (!bManualControl) ChooseIntent();
            else if ((ManualIntent==EToyIntent::Wander || ManualIntent==EToyIntent::Crawl)) EnterIntent(ManualIntent);
        }
        return;
    }
    // Progress is measured over seconds, never by per-frame random nudges.
    if (FVector::Dist2D(Toy->GetActorLocation(), LastProgressLocation) > 12)
    {
        LastProgressLocation = Toy->GetActorLocation();
        LastProgressTime = Now;
    }
    if (Now - LastProgressTime > 2.5f) Recover(TEXT("No capsule progress for 2.5 seconds"), true);
    else if (Now - MoveStarted > 18) Recover(TEXT("Move timed out"), true);
}

void AToyAIController::ChooseIntent()
{
    const auto Weight = [](float Value) { return FMath::IsFinite(Value) ? FMath::Max(0.f, Value) : 0.f; };
    const float Weights[] = {Weight(Toy->IdleWeight), Weight(Toy->WanderWeight), Weight(Toy->LookWeight), Weight(Toy->GestureWeight)};
    const float Sum = Weights[0]+Weights[1]+Weights[2]+Weights[3];
    if (Sum <= KINDA_SMALL_NUMBER) { EnterIntent(EToyIntent::Idle); return; }
    float Pick = IntentRandom.FRand() * Sum;
    for (int32 I=0; I<4; ++I)
    {
        Pick -= Weights[I];
        if (Pick < 0) { EnterIntent(static_cast<EToyIntent>(I)); return; }
    }
    EnterIntent(EToyIntent::Idle);
}

void AToyAIController::EnterIntent(EToyIntent NewIntent)
{
    Toy->SetIntent(NewIntent);
    ++IntentCounts[static_cast<int32>(NewIntent)];
    if ((NewIntent == EToyIntent::Wander || NewIntent == EToyIntent::Crawl))
    {
        FVector Goal;
        if (SampleReachableDestination(Goal)) RequestDestination(Goal);
        else { ++NavSampleFailures; Recover(TEXT("No reachable destination after 16 samples")); }
    }
    else
    {
        Pause(false);
        LastEvent = UEnum::GetValueAsString(NewIntent);
    }
}

bool AToyAIController::SampleReachableDestination(FVector& Out)
{
    UNavigationSystemV1* Nav = FNavigationSystem::GetCurrent<UNavigationSystemV1>(GetWorld());
    if (!Nav || !Toy) return false;
    const FVector Origin = Toy->GetActorLocation();
    // Seed custom sampling. Project and verify full connectivity before AI MoveTo.
    // Engine/Chaos and asynchronous nav timing are not promised deterministic.
    const float Radius = FMath::Clamp(Toy->WanderRadius, 100.f, 1500.f);
    const float LocalRadius = ConsecutiveFailures > 0 ? FMath::Min(Radius, 280.f) : Radius;
    for (int32 I=0; I<16; ++I)
    {
        const float Angle = NavigationRandom.FRandRange(-PI, PI);
        const float Distance = FMath::Sqrt(NavigationRandom.FRand()) * LocalRadius;
        const FVector Center = ConsecutiveFailures > 0 ? Origin : HomeLocation;
        const FVector Candidate = Center + FVector(FMath::Cos(Angle)*Distance, FMath::Sin(Angle)*Distance, 0);
        FNavLocation Projected;
        if (!Nav->ProjectPointToNavigation(Candidate, Projected, FVector(55,55,220))) continue;
        if (FVector::Dist2D(Projected.Location, Origin) < 100 || FVector::Dist2D(Projected.Location, HomeLocation) > Radius) continue;
        UNavigationPath* Path = Nav->FindPathToLocationSynchronously(GetWorld(), Origin, Projected.Location, Toy);
        if (Path && Path->IsValid() && !Path->IsPartial()) { Out = Projected.Location; return true; }
    }
    return false;
}

bool AToyAIController::RequestDestination(const FVector& Goal)
{
    if (!Toy || Goal.ContainsNaN()) return false;
    Destination = Goal;
    FAIMoveRequest Request;
    Request.SetGoalLocation(Goal);
    Request.SetUsePathfinding(true);
    Request.SetAllowPartialPath(false);
    Request.SetProjectGoalLocation(false); // Already projected, or deliberately invalid in the test.
    Request.SetAcceptanceRadius(24);
    Request.SetReachTestIncludesAgentRadius(false);
    Request.SetReachTestIncludesGoalRadius(false);
    NavigationState = EToyNavigationState::Moving;
    MoveStarted = LastProgressTime = GetWorld()->GetTimeSeconds();
    LastProgressLocation = Toy->GetActorLocation();
    ++MoveRequests;
    // AI MoveTo's native controller API. It owns the path follower and capsule motion.
    bIssuingMove = true;
    const FPathFollowingRequestResult Result = MoveTo(Request);
    bIssuingMove = false;
    ActiveRequest = Result.MoveId;
    if (Result.Code == EPathFollowingRequestResult::Failed) { Recover(TEXT("AI MoveTo rejected destination")); return false; }
    if (Result.Code == EPathFollowingRequestResult::AlreadyAtGoal)
    {
        ++Arrivals; ConsecutiveFailures=0; Toy->SetIntent(EToyIntent::Idle); Pause(false);
    }
    LastEvent = TEXT("Following full NavMesh path");
    return true;
}

void AToyAIController::OnMoveCompleted(FAIRequestID RequestID, const FPathFollowingResult& Result)
{
    Super::OnMoveCompleted(RequestID, Result);
    if (!Toy || bSuppressCompletion || bIssuingMove || NavigationState != EToyNavigationState::Moving || RequestID != ActiveRequest) return;
    if (Result.IsSuccess())
    {
        ++Arrivals;
        ConsecutiveFailures = 0;
        Toy->SetIntent(EToyIntent::Idle);
        Pause(false);
        LastEvent = TEXT("Arrived; pausing before next intent");
        UE_LOG(LogTemp, Display, TEXT("TOY Arrival %d at %s"), Arrivals, *Toy->GetActorLocation().ToCompactString());
    }
    else Recover(FString::Printf(TEXT("Path completion: %s"), *Result.ToString()), Result.Code == EPathFollowingResult::Blocked);
}

void AToyAIController::Pause(bool bRecovery)
{
    NavigationState = bRecovery ? EToyNavigationState::Recovering : EToyNavigationState::Paused;
    const float Low = FMath::Clamp(FMath::Min(Toy->PauseMin, Toy->PauseMax), .3f, 20.f);
    const float High = FMath::Clamp(FMath::Max(Toy->PauseMin, Toy->PauseMax), Low, 20.f);
    const float Backoff = bRecovery ? FMath::Min(5.f, .5f * ConsecutiveFailures) : 0;
    NextDecisionTime = GetWorld()->GetTimeSeconds() + IntentRandom.FRandRange(Low, High) + Backoff;
}

void AToyAIController::Recover(const FString& Reason, bool bStuck)
{
    ++PathFailures;
    if (bStuck) ++StuckRecoveries;
    ConsecutiveFailures = FMath::Min(ConsecutiveFailures+1, 10);
    bSuppressCompletion = true;
    StopMovement();
    bSuppressCompletion = false;
    Toy->GetCharacterMovement()->StopMovementImmediately();
    Toy->SetIntent(EToyIntent::Idle);
    Pause(true);
    LastEvent = Reason;
    UE_LOG(LogTemp, Display, TEXT("TOY Recovery: %s"), *Reason);
}

void AToyAIController::ForceIntent(EToyIntent NewIntent)
{
    if (!Toy || static_cast<uint8>(NewIntent)>7) return;
    bSuppressCompletion=true; StopMovement(); bSuppressCompletion=false;
    EnterIntent(NewIntent);
}

void AToyAIController::TestUnreachableDestination()
{
    if (!Toy) return;
    bSuppressCompletion=true; StopMovement(); bSuppressCompletion=false;
    Toy->SetIntent(EToyIntent::Wander);
    RequestDestination(HomeLocation + FVector(100000,100000,0));
}

void AToyAIController::SetManualIntent(EToyIntent NewIntent)
{
    if (!Toy || static_cast<uint8>(NewIntent)>7) return;
    bManualControl=true;
    ManualIntent=NewIntent;
    ForceIntent(NewIntent);
    Toy->GetCharacterMovement()->MaxWalkSpeed=NewIntent==EToyIntent::Crawl?55.f:FMath::Clamp(Toy->WalkSpeed,60.f,240.f);
    if (NewIntent!=EToyIntent::Wander && NewIntent!=EToyIntent::Crawl) Toy->GetCharacterMovement()->StopMovementImmediately();
    if (NewIntent==EToyIntent::Hop)
    {
        Toy->JumpStartZ=Toy->GetActorLocation().Z;
        Toy->MaxJumpRise=0;
        Toy->GetCharacterMovement()->JumpZVelocity=330;
        Toy->Jump();
        FTimerHandle ReleaseJump;
        GetWorldTimerManager().SetTimer(ReleaseJump,[this](){if(Toy)Toy->StopJumping();},.1f,false);
    }
}
void AToyAIController::ResumeAutonomy()
{
    bManualControl=false;
    if (Toy) Toy->GetCharacterMovement()->MaxWalkSpeed=FMath::Clamp(Toy->WalkSpeed,60.f,240.f);
    if (Toy) ForceIntent(EToyIntent::Idle);
}
