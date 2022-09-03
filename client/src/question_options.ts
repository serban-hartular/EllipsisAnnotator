export class Answer {
    answer : string
    next : Question
    constructor(answer : string, next : Question = null) {
        this.answer = answer
        this.next = next
    }
}

export default class Question {
    text : string
    options : Array<Answer>
    constructor(text : string, options : Array<Answer|string> ) {
        this.text = text
        this.options = []
        for(let option of options) {
            if(typeof(option) == 'string')
                this.options.push(new Answer(option))
            else
                this.options.push(option)
        }
    }
}