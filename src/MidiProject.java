import javax.sound.midi.*;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.OutputStream;
import java.net.Socket;
import java.net.UnknownHostException;

import static javax.sound.midi.ShortMessage.NOTE_OFF;
import static javax.sound.midi.ShortMessage.NOTE_ON;


public class MidiProject {
    private static String path = "./midis/";
    private static int port = 5000;

    public static void main(String args[]) throws UnknownHostException, IOException {
        try {
            // open socket to pass data to python script
            Socket client = new Socket("localhost", port);

            // get output stream to pass data
            OutputStream out = client.getOutputStream();

            // get synthesizer to play music
            Synthesizer synthesizer = MidiSystem.getSynthesizer();
            synthesizer.open();

            // get sequencer to read file
            Sequencer sequencer = MidiSystem.getSequencer(false);

            // add note receiver and synthesizer to get notes from sequence
            sequencer.getTransmitter().setReceiver(new NoteReceiver(out));
            sequencer.getTransmitter().setReceiver(synthesizer.getReceiver());
            sequencer.open();

            // choose midi file and play song
            sequencer.setSequence(new FileInputStream(path + "kuronuri_sekaiate_shokan.mid"));
            sequencer.start();

            // loop until midi file is completely read
            while (sequencer.isRunning()) {
                try {
                    Thread.sleep(1000);
                } catch (InterruptedException e) {
                    e.printStackTrace();
                    break;
                }
            }

            client.close();
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
    OutputStream output;

    public NoteReceiver(OutputStream output) {
        this.output = output;
    }

    @Override
    public void send(MidiMessage message, long timeStamp) {
        if (message instanceof ShortMessage) {
            ShortMessage sm = (ShortMessage) message;

            if (sm.getCommand() == NOTE_ON) {
                int key = sm.getData1();
                //Note note = new Note(key);

                try {
                    output.write((key + "\n" + "on" + "\n").getBytes());
                    output.flush();
                } catch (IOException e) {
                    throw new RuntimeException(e);
                }
                //System.out.println(System.currentTimeMillis() + " " + note + " ON");
                // press note

            } else if (sm.getCommand() == NOTE_OFF) {
                int key = sm.getData1();
                //Note note = new Note(key);

                try {
                    output.write((key + "\n" + "off" + "\n").getBytes());
                    output.flush();
                } catch (IOException e) {
                    throw new RuntimeException(e);
                }

                //System.out.println(System.currentTimeMillis() + " " + note + " OFF");
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
