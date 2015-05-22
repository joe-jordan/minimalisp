(bind 'small 0.00567)
(bind 'big 99999)
(bind 'str "Aardvark")
(bind 'str2 "Zebra")

(puts "is BIG greater than SMALL? " (if (> big small)
                                        "yes!"
                                        "no!"))

(puts "is Z greater than A? " (if (> str2 str)
                                  "yes!"
                                  "no!"))
