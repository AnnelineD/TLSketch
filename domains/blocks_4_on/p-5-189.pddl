

(define (problem BW-rand-5)
(:domain blocksworld-on)
(:objects b1 b2 b3 b4 b5 )
(:init
(arm-empty)
(on b1 b3)
(on b2 b5)
(on-table b3)
(on b4 b1)
(on b5 b4)
(clear b2)
)
(:goal
(and
(on b1 b2))
)
)


