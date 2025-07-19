import torch
LATEX_LIST=["E = m c ^2",
            "E = m c ^2",
            "E = m c ^2",
            "E = m c ^2",
            "E = m c ^2",
            "E = m c ^2",
            "E = m c ^2",
            "E = m c ^2",
            "E = m c ^2",
            "E = m c ^2",
            "E = m c ^2",
            "E = m c ^2",
            "E = m c ^2",
            "E = m c ^2",
            "E = m c ^2",    
            "E = m c ^2",
            "E = m c ^2",
            "E = m c ^2",
            "E = m c ^2",
            "E = m c ^2",
            "E = m c ^2",
            "E = m c ^2",
        ]
studentsAnswersAndScores = [
    dict(
        studentID="11451s14",
        latexList = [
            "E=m c ^2",
            "E=m c ^2",
            "E=m c ^2",
            "E=m c ^2",
            "E=m c ^2",
            "E=m c ^2",
            "E=m c ^2",
            "E=m c ^2",
            "E=m c ^2",
            "E=m c ^2",
            "E=m c ^2",
            "E=m c ^2",
            "E=m c ^2",
            "E=m c ^2",
            "E=m c ^2",
            "E=m c ^2",
            "E=m c ^2",
            "E=m c ^2",
            "E=m c ^2",
            "E=m c ^2",
        ]
    ),
    dict(
        studentID = "1919810",
        latexList = [
            "E=M c ^2",
        ]
    )
]
#torch.save(studentsAnswersAndScores,"./studentsAnswers/students_answers_for_question1.pth")
torch.save([dict(studentID=str(x),latexList = LATEX_LIST) for x in range(1000)],"./studentsAnswers/students_answers_for_question1.pth")