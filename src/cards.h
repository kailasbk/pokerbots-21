#pragma once

#include <skeleton/constants.h>
#include <map>
#include <vector>
#include <string>
#include <fmt/core.h>

using namespace pokerbots::skeleton;

constexpr std::array<char, 13> VALUES = {'2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A'};
constexpr std::array<char, 4> SUITS = {'h', 'd', 's', 'c'};
constexpr char NONE = '0';

int cton(char value, bool aceLower = false);
char ntoc(int value);

std::vector<Card> createCards(std::vector<Card> excludes);

std::vector<Card> sortCards(std::vector<Card> cards);
void sortCards(std::vector<Card>* cards_ptr);

char highestPair(std::vector<Card>, char exclude = NONE);
char highestTriple(std::vector<Card>, char exclude = NONE);
char highestQuad(std::vector<Card>);
char highestFlush(std::vector<Card>);
char highestStraight(std::vector<Card>);

std::string bestHand(std::vector<Card>);
int compareHands(std::string one, std::string two);

double MonteCarloProb(std::array<Card, 2> hole, std::vector<Card> middle, std::vector<Card> remaining);