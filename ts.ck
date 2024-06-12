 5=> int N;

for (0 => int i; i < N; i++) {

    BandedWG bwg => dac;

    2 => bwg.preset;

    (7 - i) * 55 => bwg.freq;

    (4 + i) * 5.0 / N => bwg.noteOn;

    32::second / 55 => now;

}

3 * 4 * 32::second / 55 => now;

