(bind '++ (with '(i) '(+ i 1)))

(bind 'i 0)

(puts "before while, i = " i)

(while '(< i 5)
       '(bind 'i (++ i)))

(puts "after while, i = " i)
