// ───── effspm/largebm/src/load_inst.cpp ─────────────────────────────
#include <sstream>
#include <algorithm>
#include <cmath>
#include <ctime>
#include <fstream>
#include <vector>
#include <string>

#include "load_inst.hpp"    // header with global declarations
#include "build_mdd.hpp"    // Arc & global Tree definitions
#include "utility.hpp"      // give_time()
#include "freq_miner.hpp"   // Pattern class

namespace largebm {

// ── global definitions ────────────────────────────────────────────
bool use_list      = false;
bool b_disp        = false;
bool b_write       = false;
bool use_dic       = false;
bool just_build    = false;
bool pre_pro       = false;
bool itmset_exists = false;

unsigned int        M = 0, L = 0, time_limit = 0;
unsigned long long  N = 0, num_nodes = 0, theta = 0, E = 0;
std::clock_t        start_time = 0;

std::vector<int>              item_dic;
std::vector<Pattern>          DFS;
std::vector<std::vector<int>> items;       // list‐mode working DB
std::vector<std::vector<int>> collected;   // patterns for Python
std::vector<int>              inv_item_dic;
std::string out_file, folder;
void ClearCollected()                            { collected.clear(); }
const std::vector<std::vector<int>>& GetCollected() { return collected; }

// ───────────── helper for list‐mode DB build ─────────────────────
static void Load_items_list(const std::string& fname)
{
    std::ifstream in(fname);
    if (!in.good()) {
        return;
    }
    std::string line;
    while (std::getline(in, line)) {
        std::istringstream iss(line);
        std::vector<int> seq;
        int x;
        while (iss >> x) {
            int a = std::abs(x);
            if (a < 1 || a > static_cast<int>(item_dic.size())) {
                continue;
            }
            if (item_dic[a - 1] == -1) {
                continue;
            }
            seq.push_back(x);
        }
        if (!seq.empty()) {
            items.push_back(std::move(seq));
        }
    }
}

// ─────────────── main loader ─────────────────────────────────────
bool Load_instance(const std::string& items_file, double minsup)
{
    start_time = std::clock();

    if (use_list)
    {
        if (!Preprocess(items_file, minsup)) {
            return false;
        }

        inv_item_dic.assign(L + 1, 0);
        for (int old = 1; old <= static_cast<int>(item_dic.size()); ++old) {
            int cid = item_dic[old - 1];
            if (cid > 0) inv_item_dic[cid] = old;
        }

        Load_items_list(items_file);

        N = items.size();
        theta = (minsup < 1.0)
                ? static_cast<unsigned long long>(std::ceil(minsup * N))
                : static_cast<unsigned long long>(minsup);
        return true;
    }

    std::clock_t kk = std::clock();
    Tree.clear();
    Tree.emplace_back(0, 0, 0);  // root node

    if (pre_pro) {
        if (!Preprocess(items_file, minsup)) {
            return false;
        }
        Load_items_pre(items_file);
    } else {
        Load_items(items_file);
    }

    return true;
}

// ────────────── Preprocess (list mode) ───────────────────────────
bool Preprocess(const std::string& inst, double thresh)
{
    std::ifstream file(inst);
    if (!file.good()) {
        return false;
    }

    std::vector<unsigned long long> freq(1000000);
    std::vector<unsigned long long> counted(1000000, 0);
    std::string line;
    while (std::getline(file, line)) {
        ++N;
        std::istringstream iss(line);
        int x;
        while (iss >> x) {
            int a = std::abs(x);
            L = std::max(L, static_cast<unsigned int>(a));
            if (freq.size() < L) {
                freq.resize(L);
                counted.resize(L);
            }
            if (counted[a - 1] != N) {
                freq[a - 1]++;
                counted[a - 1] = N;
            }
        }
    }

    theta = (thresh < 1.0)
            ? static_cast<unsigned long long>(std::ceil(thresh * N))
            : static_cast<unsigned long long>(thresh);

    item_dic.assign(L, -1);
    unsigned int newid = 0;
    for (unsigned int old = 1; old <= L; ++old) {
        if (freq[old - 1] >= theta) {
            ++newid;
            item_dic[old - 1] = static_cast<int>(newid);
        }
    }

    return true;
}

// Load_items_pre: MDD insert from file
void Load_items_pre(const std::string& inst_name) {
    std::ifstream file(inst_name);
    if (!file.good()) {
        return;
    }

    std::string line;
    while (std::getline(file, line)) {
        std::istringstream word(line);
        std::string itm;
        std::vector<int> temp_vec;
        bool sgn = false;
        while (word >> itm) {
            int ditem;
            try {
                ditem = std::stoi(itm);
            } catch (...) {
                continue;
            }
            int absidx = std::abs(ditem) - 1;
            if (absidx < 0 || absidx >= static_cast<int>(item_dic.size())) {
                if (!sgn && ditem < 0) sgn = true;
                continue;
            }
            if (item_dic[absidx] == -1) {
                if (!sgn && ditem < 0) sgn = true;
                continue;
            }
            if (ditem > 0) {
                ditem = item_dic[ditem - 1];
                itmset_exists = true;
            } else {
                ditem = -item_dic[-ditem - 1];
            }
            if (sgn) {
                if (ditem > 0) ditem = -ditem;
                sgn = false;
            }
            temp_vec.push_back(ditem);
        }
        if (temp_vec.empty()) {
            continue;
        }

        N++;
        M = std::max<unsigned>(M, temp_vec.size());
        Build_MDD(temp_vec);
    }
}

// Load_items: full MDD build
bool Load_items(const std::string& inst_name) {
    std::ifstream file(inst_name);
    if (!file.good()) {
        return false;
    }

    std::string line;
    while (std::getline(file, line)) {
        ++N;
        std::istringstream word(line);
        std::string itm;
        std::vector<int> temp_vec;
        while (word >> itm) {
            int ditem;
            try {
                ditem = std::stoi(itm);
            } catch (...) {
                continue;
            }
            if (ditem > 0) itmset_exists = true;
            L = std::max(L, static_cast<unsigned>(std::abs(ditem)));
            temp_vec.push_back(ditem);
        }
        M = std::max<unsigned>(M, temp_vec.size());
        Build_MDD(temp_vec);
    }
    return true;
}

} // namespace largebm
