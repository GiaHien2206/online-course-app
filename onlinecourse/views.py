from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Course, Question, Choice, Submission


@login_required
def submit(request, course_id):
    course = get_object_or_404(Course, pk=course_id)

    if request.method == "POST":
        submission = Submission.objects.create(
            user=request.user,
            course=course
        )

        questions = Question.objects.filter(
            lesson__course=course
        )

        for question in questions:
            choice_id = request.POST.get(
                f"question_{question.id}"
            )

            if choice_id:
                choice = get_object_or_404(
                    Choice,
                    pk=choice_id,
                    question=question
                )

                submission.choices.add(choice)

        return redirect(
            "onlinecourse:show_exam_result",
            course_id=course.id,
            submission_id=submission.id
        )

    return redirect(
        "onlinecourse:course_details",
        course_id=course.id
    )


@login_required
def show_exam_result(request, course_id, submission_id):
    course = get_object_or_404(
        Course,
        pk=course_id
    )

    submission = get_object_or_404(
        Submission,
        pk=submission_id,
        user=request.user
    )

    selected_choices = submission.choices.all()

    score = 0
    total = 0
    results = []

    questions = Question.objects.filter(
        lesson__course=course
    )

    for question in questions:
        total += question.grade

        selected_choice = selected_choices.filter(
            question=question
        ).first()

        correct = (
            selected_choice is not None
            and selected_choice.is_correct
        )

        if correct:
            score += question.grade

        results.append({
            "question": question,
            "selected_choice": selected_choice,
            "correct": correct,
        })

    context = {
        "course": course,
        "submission": submission,
        "score": score,
        "total": total,
        "results": results,
    }

    return render(
        request,
        "onlinecourse/exam_result.html",
        context
    )
        request,
        "onlinecourse/exam_result.html",
        context
    )
