package main

import (
	"strings"

	"golang.org/x/tour/wc"
)

func WordCount(s string) map[string]int {
	fields := strings.Fields(s)
	wordCount := make(map[string]int)
	for _, filed := range fields {
		wordCount[filed]++
	}
	return wordCount
}

func main() {
	wc.Test(WordCount)
}
