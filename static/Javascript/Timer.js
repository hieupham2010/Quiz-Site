window.addEventListener('load' , ()=> {
    var time = document.getElementById('time').value
    var second = 0
    var timer = setInterval(() => {
        if(second === 0) {
            second = 60
            time -= 1
        }
        second -= 1
        m = time
        s = second
        if(time < 10) {
            m = '0' + time
        }
        if(second < 10) {
            s = '0' + second
        }
        document.getElementById("timer").innerHTML = 'Time: ' + m + ' : ' + s
        if(second === 0 && time === 0) {
            clearInterval(timer)
            document.getElementById('form-question').submit()
        }
    } , 1000)
})