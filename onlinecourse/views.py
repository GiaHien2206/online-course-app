from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

from .models import Course, Question, Choice, Submission


@login_required
def submit(request, course_id):
    course = get_object_or_404(Course, pk=course_id)

    if request.method == "POST":

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

                Submission.objects.update_or_create(
                    user=request.user,
                    question=question,
                    defaults={
                        "choice": choice
                    }
                )

        return redirect(
            "onlinecourse:show_exam_result",
            course_id=course.id
        )

    return redirect(
        "onlinecourse:course_details",
        course_id=course.id
    )


@login_required
def show_exam_result(request, course_id):

    course = get_object_or_404(
        Course,
        pk=course_id
    )

    submissions = Submission.objects.filter(
        user=request.user,
        question__lesson__course=course
    ).select_related(
        "question",
        "choice"
    )

    score = 0
    total = 0
    results = []

    for submission in submissions:

        total += submission.question.grade

        correct = submission.choice.is_correct

        if correct:
            score += submission.question.grade

        results.append({
            "question": submission.question,
            "selected_choice": submission.choice,
            "correct": correct
        })

    passed = total > 0 and score >= total * 0.7

    context = {
        "course": course,
        "score": score,
        "total": total,
        "passed": passed,
        "results": results,
    }

    return render(
        request,
        "onlinecourse/exam_result.html",
        context
    )
