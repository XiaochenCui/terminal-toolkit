package main

import (
	"fmt"
	"math"
	"time"
)

func main() {
	t := time.Unix(9224318016000, 0)
	fmt.Printf("t: %v\n", t)

	PGEpochJDate := time.Date(2000, 1, 1, 0, 0, 0, 0, time.UTC)

	diff := t.Sub(PGEpochJDate)
	fmt.Printf("diff: %v\n", diff)
	fmt.Printf("diff: %v\n", diff.Microseconds())

	fmt.Printf("math.MaxInt64: %v\n", math.MaxInt64)

	t = PGEpochJDate
	for i := 0; i < 1000; i++ {
		t = t.Add(time.Duration(math.MaxInt64))
	}
	fmt.Printf("t: %v\n", t)
	fmt.Printf("t.Unix: %v\n", t.Unix())
	fmt.Printf("t.UnixNano: %v\n", t.UnixNano())

	getBinaryStr("2004-10-19 10:23:54")

	getBinary(time.Unix(9224318016000, 0))
	// "294277-01-01 00:00:00"
}

func getBinaryStr(tStr string) {
	t, err := time.Parse("2006-01-02 15:04:05", tStr)
	if err != nil {
		fmt.Printf("err: %v\n", err)
		return
	}
	getBinary(t)
}

func getBinary(t time.Time) {
	fmt.Printf("=== getBinary, t: %v\n", t)

	tStr := fmt.Sprint(t)

	textAsBinary := []byte(tStr)
	fmt.Printf("textAsBinary: %v\n", textAsBinary)

	PGEpochJDate := time.Date(2000, 1, 1, 0, 0, 0, 0, time.UTC)

	diff := t.Sub(PGEpochJDate).Microseconds()
	fmt.Printf("diff (microseconds): %v\n", diff)

	// get big endian binary representation of diff
	binaryDiff := make([]byte, 8)
	for i := 0; i < 8; i++ {
		binaryDiff[i] = byte(diff >> uint(8*(7-i)))
	}
	fmt.Printf("binaryDiff: %v\n", binaryDiff)
}
