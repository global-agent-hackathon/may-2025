import random
import chess
import chess.engine
import time
import json

def generate_mate_in_n_puzzle():
    POPULATION_SIZE = 20
    GENERATIONS = 5
    MUTATION_RATE = 0.5
    ENGINE_DEPTH = 20  # Stockfish analysis depth
    TARGET_MATE_DEPTH = [1,2,3,4,5,6] 
    engine_path="stockfish/stockfish"

    STARTING_POSITIONS = [
        "r1bqk2r/ppp2ppp/2n2n2/4p3/2B1P3/2N2N2/PPPP1PPP/R1BQ1RK1 b kq - 2 6",  # Italian Game middlegame
        "r1bqk2r/ppp2ppp/2n2n2/3pp3/1b2P3/2N2N2/PPPP1PPP/R1BQKB1R w KQkq - 2 7",  # Ruy Lopez middlegame
        "rnbqkb1r/pp2pppp/5n2/3p4/3P4/2N2N2/PPP1PPPP/R1BQKB1R w KQkq - 3 6",  # Queen's Gambit declined
        "rnbqk2r/ppp2ppp/3p1n2/8/3NP3/2N5/PPP1PPPP/R1BQKB1R w KQkq - 0 9", 
        "rnbqkb1r/pp3ppp/3p1n2/8/3NP3/2N5/PPP2PPP/R1BQKB1R w KQkq - 0 9", 
        "r4rk1/pp4pp/2n5/8/3p4/2N2N2/PPP3PP/R4RK1 w - - 2 25",
        "r2q1rk1/pp1bppbp/2np1np1/8/3NP3/2N1BP2/PPPQ2PP/2KR1B1R w - - 0 10",  
        "rnbqkb1r/pp2pppp/5n2/3p4/3P4/2N2N2/PPP1PPPP/R1BQKR2 b kq - 2 8",  
        "rnbqkb1r/pp2pp1p/3p1np1/8/3NP3/2N5/PPP2PPP/R1BQKB1R w KQkq - 0 10",  
        "r1bqk2r/ppp2ppp/2n5/3pp3/1b2P3/2N2N2/PPPP1PPP/R1BQKB1R w KQkq - 0 8",  
    ]
    # Initialize Stockfish
    engine = None
    try:
        engine = chess.engine.SimpleEngine.popen_uci(engine_path)
        print("Stockfish engine initialized successfully")
    except Exception as e:
        print(f"Error initializing Stockfish: {e}")
        exit(1)

    def random_board_from_start(fen=None):
        if fen:
            board = chess.Board(fen)
        else:
            board = chess.Board()

        moves = random.randint(5, 10)
        capture_count = 0

        for _ in range(moves):
            if board.is_game_over():
                break
            legal_moves = list(board.legal_moves)
            if not legal_moves:
                break

            tactical_moves = [move for move in legal_moves if board.is_capture(move) or board.gives_check(move)]
    
            if capture_count >= 3:
                # After 3 captures, prefer non-captures to stabilize position
                non_tactical_moves = [move for move in legal_moves if move not in tactical_moves]
                move = random.choice(non_tactical_moves) if non_tactical_moves else random.choice(legal_moves)
            else:
                if tactical_moves and random.random() < 0.7:
                    move = random.choice(tactical_moves)
                    if board.is_capture(move):
                        capture_count += 1
                else:
                    move = random.choice(legal_moves)

            board.push(move)

        return board

    def evaluate_board(board):
        """Evaluate the board: specifically targeting mate in 2-3 moves."""
        if board.is_game_over():
            return 0  # We don't want already finished positions

        try:
            # Analyze with Stockfish
            result = engine.analyse(board, chess.engine.Limit(depth=ENGINE_DEPTH))
            score = result['score'].relative
    
            # Check for mate sequences
            if score.is_mate():
                mate_in = score.mate()
                if mate_in is not None and mate_in > 0:
                    # We're specifically looking for mate in 2 or 3
                    if mate_in in TARGET_MATE_DEPTH:
                        # Give higher score for mate-in-2 than mate-in-3
                        return 1000 - mate_in * 10  # 980 for mate-in-2, 970 for mate-in-3
                    # Give some credit to other mates but less
                    return 500 - mate_in * 10
    
            # For non-mate positions, give some credit to tactical positions
            tactical_score = 0
    
            # Count checks
            checks = sum(1 for move in board.legal_moves if board.gives_check(move))
            tactical_score += checks * 5
    
            # Count pieces under attack
            attacked_pieces = 0
            for square in chess.SQUARES:
                piece = board.piece_at(square)
                if piece and board.is_attacked_by(not board.turn, square):
                    if piece.piece_type == chess.KING:
                        tactical_score += 30  # King under attack is good for tactics
                    else:
                        attacked_pieces += 1
            tactical_score += attacked_pieces * 3
    
            # Reward positions that are roughly equal
            cp_score = score.score()
            if cp_score is not None:
                if -200 < cp_score < 200:
                    tactical_score += 30  # Balanced positions
        
            return tactical_score
    
        except Exception as e:
            print(f"Error during evaluation: {e}")
            return 0

    def mutate(board, visited_positions=None):
        """Apply some random changes to the board position without undoing moves."""
        if visited_positions is None:
            visited_positions = set()

        new_board = board.copy()

        # Different mutation strategies
        mutation_type = random.randint(1, 2)  # Limiting to only forward mutations

        if mutation_type == 1:
            # Make 1-2 random moves
            for _ in range(random.randint(1, 2)):
                if not new_board.is_game_over():
                    legal_moves = list(new_board.legal_moves)
                    if legal_moves:
                        # Prefer tactical moves
                        tactical_moves = [move for move in legal_moves if 
                                        new_board.is_capture(move) or 
                                        new_board.gives_check(move)]
                        if tactical_moves:
                            move = random.choice(tactical_moves)
                        else:
                            move = random.choice(legal_moves)
                        new_board.push(move)
            
                    # Check if this position has already been visited
                    if new_board.fen() in visited_positions:
                        new_board.pop()  # Undo the move if it creates a repeat position
                        continue

                    # Add the new position to the visited set
                    visited_positions.add(new_board.fen())

        else:
            # Make a tactical move if possible
            if not new_board.is_game_over():
                legal_moves = list(new_board.legal_moves)
                tactical_moves = [move for move in legal_moves if 
                                new_board.is_capture(move) or 
                                new_board.gives_check(move)]
                if tactical_moves:
                    move = random.choice(tactical_moves)
                    new_board.push(move)
                elif legal_moves:
                    move = random.choice(legal_moves)
                    new_board.push(move)

                # Check if this position has already been visited
                if new_board.fen() in visited_positions:
                    new_board.pop()  # Undo the move if it creates a repeat position
                else:
                    visited_positions.add(new_board.fen())

        return new_board

    def crossover(board1, board2):
        """Mix two boards by taking some moves from each."""
        try:
            # Start with a common position
            new_board = chess.Board(board1.starting_fen)
    
            # Get moves from both boards
            moves1 = list(board1.move_stack)
            moves2 = list(board2.move_stack)
    
            # Choose a crossover point
            split1 = random.randint(0, len(moves1))
    
            # Apply moves from first board up to crossover point
            for move in moves1[:split1]:
                if move in new_board.legal_moves:
                    new_board.push(move)
                else:
                    break
    
            # Then apply some moves from second board if possible
            if len(moves2) > 0:
                # Try to apply 1-3 moves from board2
                move_count = random.randint(1, min(3, len(moves2)))
                for move in moves2[:move_count]:
                    if move in new_board.legal_moves:
                        new_board.push(move)
                    else:
                        break
            
            return new_board
        except Exception as e:
            print(f"Error during crossover: {e}")
            # Return one of the parents as fallback
            return board1.copy()

    def genetic_algorithm(starting_fen=None):
        # Create initial population
        population = [random_board_from_start(starting_fen) for _ in range(POPULATION_SIZE)]

        best_overall_fitness = 0
        best_overall_board = None
        best_analysis = None

        for generation in range(GENERATIONS):
            print(f"Generation {generation+1}/{GENERATIONS}...")

            # Evaluate fitness
            fitness_scores = []
            for i, board in enumerate(population):
                score = evaluate_board(board)
                fitness_scores.append((score, board))
                print(f"Board {i+1}: Fitness {score}")

            # Sort by fitness
            fitness_scores.sort(reverse=True, key=lambda x: x[0])
            best_fitness, best_board = fitness_scores[0]

            # Keep track of best overall
            if best_fitness > best_overall_fitness:
                best_overall_fitness = best_fitness
                best_overall_board = best_board.copy()
                print(f"New best fitness: {best_overall_fitness}")
        
                # Check for mate in specified moves
                try:
                    result = engine.analyse(best_overall_board, chess.engine.Limit(depth=ENGINE_DEPTH))
                    best_analysis=result
                    score = result['score'].relative
                    if score.is_mate() and score.mate() in TARGET_MATE_DEPTH:
                        print(f"Found mate in {score.mate()} position!")
                        print(best_overall_board.fen())
                        print(best_overall_board)
                except Exception as e:
                    print(f"Error analyzing best board: {e}")

            print(f"Best fitness in generation {generation+1}: {best_fitness}")

            # Early stopping if we find a very good candidate
            if best_fitness >= 970:  # This should be a mate in target depth
                print("Excellent puzzle found! Early stopping.")
                break

            # Select top 50% to breed
            survivors = [board for _, board in fitness_scores[:POPULATION_SIZE//2]]
            if not survivors:
                print("No survivors with positive fitness. Regenerating population.")
                population = [random_board_from_start(starting_fen) for _ in range(POPULATION_SIZE)]
                continue

            # Create next generation
            new_population = []
            # Always keep the best board
            new_population.append(best_board.copy())
    
            # Sometimes introduce fresh blood
            if random.random() < 0.1:  # 10% chance
                new_population.append(random_board_from_start(starting_fen))
    
            while len(new_population) < POPULATION_SIZE:
                parent1 = random.choice(survivors)
                parent2 = random.choice(survivors)
                child = crossover(parent1, parent2)
                if random.random() < MUTATION_RATE:
                    child = mutate(child)
                new_population.append(child)

            population = new_population

        # Return the best board found in any generation
        return best_overall_board, best_overall_fitness,best_analysis

    def verify_mate_in_n(board, n):
        """Verify if the position actually has a mate in n moves."""
        result = engine.analyse(board, chess.engine.Limit(depth=ENGINE_DEPTH))
        score = result['score'].relative

        solution_data = {
            "is_mate_in_n": False,
            "first_move": None,
            "solution_sequence": [],
            "board_after_first_move": None
        }


        if score.is_mate() and score.mate() == n:
            # Find the best move
            best_move = engine.play(board, chess.engine.Limit(depth=ENGINE_DEPTH)).move
            solution_data["is_mate_in_n"] = True
            solution_data["first_move"] = str(best_move)
            solution_data["solution_sequence"].append(str(best_move))
    
    
            # Play the first move
            board_copy = board.copy()
            board_copy.push(best_move)
            solution_data["board_after_first_move"] = str(board_copy)

            # If there's only one legal response, add it to the sequence
            if not board_copy.is_game_over():
                legal_responses = list(board_copy.legal_moves)
                if len(legal_responses) == 1:
                    response_move = legal_responses[0]
                    board_copy.push(response_move)
                    solution_data["solution_sequence"].append(str(response_move))
                    
                    # If not checkmate yet, find the final checkmate move
                    if not board_copy.is_game_over():
                        final_move = engine.play(board_copy, chess.engine.Limit(depth=ENGINE_DEPTH)).move
                        board_copy.push(final_move)
                        solution_data["solution_sequence"].append(str(final_move))
            
            return solution_data
        
        return solution_data
    

    start_time = time.time()
    starting_fen = random.choice(STARTING_POSITIONS)
    print(f"Starting from FEN: {starting_fen}")

    best_board, fitness, analysis = genetic_algorithm(starting_fen)
    end_time = time.time()

    print("\nGenerated FEN:", best_board.fen())
    print("Fitness Score:", fitness)
    print(f"Total Time: {round(end_time - start_time, 2)} seconds")

    # Print out a visualization of the board
    print("\nBoard visualization:")
    board = chess.Board(best_board.fen())
    print(board)

    # Provide Stockfish's assessment of the position
    analysis = engine.analyse(board, chess.engine.Limit(depth=ENGINE_DEPTH))
    print(f"\nStockfish evaluation: {analysis['score']}")

    actual_mate_depth = None
    solution_data = None

    for n in range(1, 7):
        potential_solution = verify_mate_in_n(best_board, n)
        if potential_solution["is_mate_in_n"]:
            print("solution: ", potential_solution)
            actual_mate_depth = n
            solution_data = potential_solution
            break

    if solution_data["is_mate_in_n"]:
        print(f"Successfully generated a mate in {actual_mate_depth} puzzle!")
    else:
        print(f"Warning: The puzzle is not actually a mate in {actual_mate_depth} moves.")
        
    # Package the result data to return
    result_data = {
        "fen": best_board.fen(),
        "side_to_move": "White" if best_board.turn else "Black",
        "mate_in": actual_mate_depth,
        "first_move": solution_data["first_move"] if solution_data else None,
        "solution_sequence": solution_data["solution_sequence"] if solution_data else [],
        "board_after_first_move": solution_data["board_after_first_move"] if solution_data else None,
        "fitness": fitness
    }
    engine.quit()
    
    # Return the structured data instead of just printing
    return json.dumps(result_data)        