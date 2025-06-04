import javax.sound.midi.*;
import java.io.FileInputStream;
import java.io.IOException;

import static javax.sound.midi.ShortMessage.NOTE_OFF;
import static javax.sound.midi.ShortMessage.NOTE_ON;


public class MidiProject {
    public static void main(String args[]) {
        try {
            Synthesizer synthesizer = MidiSystem.getSynthesizer();
            synthesizer.open();
            Sequencer sequencer = MidiSystem.getSequencer(false);
            sequencer.getTransmitter().setReceiver(new NoteReceiver());
            sequencer.getTransmitter().setReceiver(synthesizer.getReceiver());
            sequencer.open();
            sequencer.setSequence(new FileInputStream("repeat test.mid"));
            sequencer.start();

            while (sequencer.isRunning()) {
                try {
                    Thread.sleep(1000);
                } catch (InterruptedException e) {
                    e.printStackTrace();
                    break;
                }
            }

            sequencer.close();
            synthesizer.close();
        } catch (InvalidMidiDataException e) {
            throw new RuntimeException(e);
        } catch (MidiUnavailableException e) {
            throw new RuntimeException(e);
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
    }
}

class NoteReceiver implements Receiver {
    @Override
    public void send(MidiMessage message, long timeStamp) {
        if (message instanceof ShortMessage) {
            ShortMessage sm = (ShortMessage) message;
            int channel = sm.getChannel();

            if (sm.getCommand() == NOTE_ON) {
                int key = sm.getData1();
                int velocity = sm.getData2();
                Note note = new Note(key);
                System.out.println(System.currentTimeMillis() + " " + note + " ON");
                // press note

            } else if (sm.getCommand() == NOTE_OFF) {
                int key = sm.getData1();
                int velocity = sm.getData2();
                Note note = new Note(key);
                System.out.println(System.currentTimeMillis() + " " + note + " OFF");
                // release note
            } else {
                //System.out.println("Command:" + sm.getCommand());
            }
        }
    }

    @Override
    public void close() {

    }
}

class Note {
    private static final String[] NOTE_NAMES = {"C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"};

    private String name;
    private int key;
    private int octave;

    public Note(int key) {
        this.key = key;
        this.octave = (key / 12) - 1;
        int note = key % 12;
        this.name = NOTE_NAMES[note];
    }

    @Override
    public boolean equals(Object obj) {
        return obj instanceof Note && this.key == ((Note) obj).key;
    }

    @Override
    public String toString() {
        return this.name + this.octave + " key=" + this.key;
    }
}
